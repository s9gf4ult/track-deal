#!/bin/env python
# -*- coding: utf-8 -*-
## sconnection ##

import sqlite3
from common_methods import *
import datetime
import time

class scon_cursor(object):
    """
    Attributes:
    _query = None
    _connection = None
    _arguments = None
    """
    ##############
    # Attributes #
    ##############
    _query = None
    _connection = None
    _arguments = None
    
    ###########
    # Methods #
    ###########

    def fetchall(self, ):
        """fetch all hash tables
        """
        ret = []
        for x in self:
            ret.append(x)
        return ret

    
    def __init__(self, connection, query, arguments):
        """initializes cursor
        
        Arguments:
        - `cursor`:
        """
        self._arguments = arguments
        self._query = query
        self._connection = connection

    def __iter__(self, ):
        """start iteration
        """
        if self._arguments != None:
            return scon_iter(self._connection.execute(self._query, self._arguments))
        else:
            return scon_iter(self._connection.execute(self._query))

class scon_iter(object):
    """iterator returning hashes on query results
    Attributes:
    _cursor = None
    """
    ##############
    # Attributes #
    ##############
    _cursor = None
    _names = []
    _iter = None
    ###########
    # Methods #
    ###########
    
    def __init__(self, cursor):
        """
        
        Arguments:
        - `cursor`:
        """
        self._cursor = cursor
        self._names = map(lambda a: a[0], self._cursor.description)
        self._iter = self._cursor.__iter__()

    def next(self, ):
        """return next hash
        """
        ret = {}
        nextval = self._iter.next()
        for x in xrange(0, len(self._names)):
            ret[self._names[x]] = nextval[x]
        return ret

        


        


class sconnection(sqlite3.Connection):
    """wrapper over sqlite connection
    implementing some usefull things
    Attributes:
    
    """
    ##############
    # Attributes #
    ##############
    
    
    ###########
    # Methods #
    ###########
    def __init__(self, connect_string):
        """initializes connection and makes some other things
        
        Arguments:
        - `connect_string`:
        """
        sqlite3.register_adapter(str, lambda a: a.decode(u'utf-8'))
        sqlite3.register_adapter(datetime.datetime, lambda a: time.mktime(a.timetuple()))
        sqlite3.register_adapter(datetime.date, lambda a: time.mktime(a.timetuple()))
        sqlite3.register_adapter(datetime.time, lambda a: int(a.hour * 3600 + a.minute * 60 + a.second))
        sqlite3.register_adapter(datetime.timedelta, lambda a: a.days * 3600 * 24 + a.seconds)
        sqlite3.register_converter('datetime', any_to_datetime)
        sqlite3.register_converter("date", any_to_date)
        sqlite3.register_converter("time", any_to_time)
        sqlite3.register_converter("timedelta", any_to_timedelta)

        super(sconnection, self).__init__(connect_string, detect_types = sqlite3.PARSE_DECLTYPES)
        self.execute("pragma foreign_keys=on")
        self.create_function("argument_value", 2, argument_value)
        self.create_aggregate("string_reduce", 1, string_reduce)
        


    def insert(self, table, fields):
        """inserts data in fields into table
        
        Arguments:
        - `table`:
        - `fields`: must be hash like that {"field_name" : data_to_insert} or list of that hashes
        """
        assert(isinstance(fields, dict) or hasattr(fields, "__iter__"))
        names = set()
        for kk in (isinstance(fields, dict) and [fields] or fields):
            for k in kk.keys():
                assert(isinstance(k, basestring))
                names.add(k)
        names = sorted(names)
                    
        if isinstance(fields, dict):
            data = map(lambda a: fields[a], names)
        else:
            data = map(lambda a: map(lambda x: gethash(a, x), names), fields)
        qqs = reduce_by_string(", ", map(lambda a: "?", names))
        nns = reduce_by_string(", ", names)
        query = "insert into {0}({1}) values ({2})".format(table, nns, qqs)
        if isinstance(fields, dict):
            return self.execute(query, data)
        else:
            return self.executemany(query, data)
            

    def execute_select(self, query, arguments = None):
        """execute's query and returns iterable
        object which returns hash tables like that {"field_name" : data}
        
        Arguments:
        - `query`:
        - `arguments`:
        """
        assert(isinstance(query, basestring))
        return scon_cursor(self, query, arguments)

    def update(self, table, set_fields, where_part = None, where_arguments = []):
        """executes update on all `set_fields` where `where_part`
        
        Arguments:
        - `table`:
        - `set_fields`: hash like {"id" : value}
        - `where_part`: string
        - `where_arguments`: list of arguments in query for `where` part
        """
        assert(isinstance(set_fields, dict) or hasattr(set_fields, "__iter__"))
        names = []
        data = []
        for htb in (isinstance(set_fields, dict) and [set_fields] or set_fields):
            nn = htb.keys()
            names.append(nn)
            data.append(map(lambda a: htb[a], nn) + where_arguments)

        for (name, dd) in map(lambda a, b: (a, b), names, data):
            q = "update {0} set {1}".format(table, reduce_by_string(", ", map(lambda a: "{0} = ?".format(a), name)))
            if not is_null_or_empty(where_part):
                q += "where {0}".format(where_part)
            self.execute(q, dd)

    def begin_transaction(self, ):
        """Begins transaction
        """
        self.execute("begin transaction")

    def execute_select_cond(self, tablename, selects = ["*"], wheres = [], order_by = []):
        """generates query for execute_select pass it to
        Arguments:
        - `tablename`: string with table name
        - `selects`: [* | field name | expression | (field name | expression, alias)]
        - `wheres`: [(= | < | > | ... | 'between', exp1, exp2, exp3 ...)]
        - `order_by`: [field name]
        """
        q = u"select {0} from {1}".format(format_select_part(selects), tablename)
        (whpart, adarg) = format_where_part(wheres)
        if not is_null_or_empty(whpart):
            q += " where {0}".format(whpart)
        q += order_by_print(order_by)
        if len(adarg) > 0:
            return self.execute_select(q, adarg)
        else:
            return self.execute_select(q)
