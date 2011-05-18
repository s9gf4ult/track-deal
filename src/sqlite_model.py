#!/bin/env python
# -*- coding: utf-8 -*-
## sqlite_model ##

from common_model import common_model
from common_view import common_view
from sconnection import sconnection
from common_methods import *
from exceptions import *

class sqlite_model(common_model):
    """
    stores data in sqlite
    :Attributes:
       _connection_string = None
       _sqlite_connection = None
    """
    ##############
    # Attributes #
    ##############
    _connection_string = None
    _sqlite_connection = None
    
    
    ###########
    # Methods #
    ###########
    
    def __init__(self, ):
        """new instance of sqlite_model
        """
        pass

    @raise_db_opened
    def connect(self, connection_string):
        """connects to file or memory
        
        Arguments:
        - `connection_string`:
        """
        assert(isinstance(connection_string, basestring))
        self._connection_string = connection_string
        self._sqlite_connection = sconnection(connection_string)

    @raise_db_closed
    def dbinit(self, ):
        """
        initializes new database
        """
        with open('./sqlite/dbinit.sql') as ofile:
            self._sqlite_connection.executescript(ofile.read())

    @raise_db_closed
    def dbtemp(self, ):
        """
        initalizes temporary objects in database
        """
        with open('./sqlite/dbtemp.sql') as ofile:
            self._sqlite_connection.executescript(ofile.read())

    @raise_db_opened
    def open_existing(self, filename):
        """
        Opens existing database from file
        Arguments:
        - `filename`:
        """
        self.connect(filename)
        self.dbtemp()

    @raise_db_opened
    def create_new(self, filename):
        """Creates new empty database
        Arguments:
        - `filename`:
        """
        self.connect(filename)
        self.dbinit()
        self.dbtemp()


    @raise_db_closed
    def disconnect(self, ):
        """Disconnects from the database
        """
        self._sqlite_connection.close()
        self._sqlite_connection=None


    @raise_db_closed
    def begin_transaction(self, ):
        """Begins transaction
        """
        self._sqlite_connection.begin_transaction()

    @raise_db_closed
    def commit(self, ):
        """Commits
        """
        self._sqlite_connection.commit()

    @raise_db_closed
    def rollback(self, ):
        """Rollback
        """
        self._sqlite_connection.rollback()

    @raise_db_closed
    @in_transaction
    def add_global_data(self, parameters):
        """adds global data and
        Arguments:
        - `parameters`: hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("global_data", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names))) 

    @raise_db_closed
    def get_global_data(self, name):
        """returns value of global data or None if there is no one
        Arguments:
        - `name`:
        """
        ret = self._sqlite_connection.execute_select("select value from global_data where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

    @raise_db_closed
    @in_transaction
    def remove_global_data(self, name):
        """Removes global parameters
        Arguments:
        - `name`: string or list of strings to remove
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from global_data where name = ?", name)

    @raise_db_closed
    def list_global_data(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from global_data"))

    @raise_db_closed
    @in_transaction
    def add_database_attributes(self, parameters):
        """adds database attributes and
        Arguments:
        - `parameters`: hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("database_attributes", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names))) 

    @raise_db_closed
    def get_database_attribute(self, name):
        """returns value of global parameter or None if there is no one
        Arguments:
        - `name`:
        """
        ret = self._sqlite_connection.execute_select("select value from database_attributes where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

    @raise_db_closed
    @in_transaction
    def remove_database_attribute(self, name):
        """Removes global parameters
        Arguments:
        - `name`: string or list of strings to remove
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from database_attributes where name = ?", name)

    @raise_db_closed
    def list_database_attributes(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from database_attributes"))
    
    @raise_db_closed
    @in_transaction
    def create_paper(self, type, name, stock = None, class_name = None, full_name = None):
        """creates new paper and returns it's id
        
        Arguments:
        - `type`:
        - `name`:
        - `stock`:
        - `class_name`:
        - `full_name`:
        """
        return self._sqlite_connection.insert("papers", {"type" : type,
                                                         "stock" : stock,
                                                         "class" : class_name,
                                                         "name" : name,
                                                         "full_name" : full_name}).lastrowid

    @raise_db_closed
    def get_paper(self, type_or_id, name = None):
        """returns paper by name or by id
        if there is no one returns None
        Arguments:
        - `type_or_id`:
        """
        ret = None
        if isinstance(type_or_id, basestring) and not is_null_or_empty(name):
            ret = self._sqlite_connection.execute_select("select * from papers where type = ? and name = ?", [type_or_id, name]).fetchall()
        elif isinstance(type_or_id, int):
            ret = self._sqlite_connection.execute_select("select * from papers where id = ?", [type_or_id]).fetchall()
        else:
            raise od_exception("get_paper: wrong arguments")
        return (len(ret) > 0 and ret[0] or None)

    @raise_db_closed
    @in_transaction
    @remover_decorator("papers", {int : "id"})
    def remove_paper(self, type_or_id, name = None):
        """Removes one paper by type and name or many papers by id
        
        Arguments:
        - `type_or_id`:
        - `name`:
        """
        if isinstance(type_or_id, basestring) and isinstance(name, basestring) and not is_null_or_empty(name):
            self._sqlite_connection.execute("delete from papers where type = ? and name = ?", [type_or_id, name])

    @raise_db_closed
    def list_papers(self, order_by = []):
        """Returns list of papers
        """
        q = "select * from papers"
        if len(order_by) > 0:
            q += "order by {0}".format(reduce_by_string(", ", order_by))
        return self._sqlite_connection.execute_select(q)


    @raise_db_closed
    @in_transaction
    def create_candles(self, paper_id, candles):
        """Creates one or several candles of paper `paper_id`
        Arguments:
        - `paper_id`:
        - `candles`: hash table with keys, [duration, open_datetime, close_datetime, open_value, close_value, min_value, max_value, volume, value_type] or the list of tables
        """
        candles = (isinstance(candles, dict) and [candles] or candles)
        for candle in candles:
            candle["paper_id"] = paper_id
            assert(candle["min_value"] <= candle["open_value"] <= candle["max_value"])
            assert(candle["min_value"] <= candle["close_value"] <= candle["max_value"])
            assert(candle["open_datetime"] < candle["close_datetime"])
            assert(isinstance(candle["duration"], basestring,))
        self._sqlite_connection.insert("candles", candles)
        

    @raise_db_closed
    def get_candle(self, candle_id):
        """Get candle by id
        Arguments:
        - `candle_id`:
        """
        ret = self._sqlite_connection.execute_select("select * from candles where id = ?", [candle_id]).fetchall()
        return (len(ret) > 0 and ret[0] or None)

    @raise_db_closed
    @in_transaction
    @remover_decorator("candles", {int : "id"})
    def remove_candle(self, candles_id):
        """removes one or more candles
        Arguments:
        - `candles_id`: int or list of ints
        """
        pass

    @raise_db_closed
    def list_candles(self, paper_id, order_by = []):
        """Return ordered list of candles
        Arguments:
        - `paper_id`:
        - `order_by`:
        """
        q = "select * from candles where paper_id = ?"
        if len(order_by) > 0:
            q += "order by {0}".format(reduce_by_string(", ", order_by))
        return self._sqlite_connection.execute_select(q, [paper_id])


    @raise_db_closed
    @in_transaction
    def create_money(self, name, full_name = None):
        """Creates new money and return it's id
        Arguments:
        - `name`:
        - `full_name`:
        """
        return self._sqlite_connection.insert("moneys", {"name" : name,
                                                         "full_name" : full_name}).lastrowid

    @raise_db_closed
    def get_money(self, name_or_id):
        """Returns money object by id or name
        Arguments:
        - `name_or_id`:
        """
        if isinstance(name_or_id, basestring):
            ret = self._sqlite_connection.execute_select("select * from moneys where name = ?", [name_or_id]).fetchall()
        elif isinstance(name_or_id, int):
            ret = self._sqlite_connection.execute_select("select * from moneys where id = ?", [name_or_id]).fetchall()
        else:
            raise od_exception("get_money: incorrect parameters")
        
        return (len(ret) > 0 and ret[0] or None)

    @raise_db_closed
    @in_transaction
    @remover_decorator("moneys", {int : "id", basestring : "name"})
    def remove_money(self, name_or_id):
        """Removes money by name or by id
        Arguments:
        - `name_or_id`:
        """
        pass

    @raise_db_closed
    def list_moneys(self, order_by = []):
        """return list of moneys
        """
        q = "select * from moneys{0}".format((len(order_by) > 0 and " order by {0}".format(reduce_by_string(", ", order_by))  or ""))
        return self._sqlite_connection.execute_select(q)
    
    @raise_db_closed
    @in_transaction
    def create_point(self, paper_id, money_id, point, step):
        """Creates point explanation and return it's id
        Arguments:
        - `paper_id`:
        - `money_id`:
        - `point`:
        - `step`:
        """
        return self._sqlite_connection.insert("points", {"paper_id" : paper_id, "money_id" : money_id, "point" : point, "step" : step}).lastrowid

    @raise_db_closed
    def list_points(self, money_id = None, order_by = []):
        """Return list of points
        Arguments:
        - `money_id`:
        - `order_by`:
        """
        q = "select * from points"
        if money_id != None:
            q += " where money_id = ?"
        if len(order_by) > 0:
            q += " order by {0}".format(reduce_by_string(", ", order_by))
        if money_id != None:
            return self._sqlite_connection.execute_select(q, [money_id])
        else:
            return self._sqlite_connection.execute_select(q)

    @raise_db_closed
    def get_point(self, id_or_paper_id, money_id = None):
        """Returns point explanation by id or by paper_id and money_id
        Arguments:
        - `id_or_paper_id`:
        - `money_id`:
        """
        if money_id != None:
            ret = self._sqlite_connection.execute_select("select * from points where paper_id = ? and money_id = ?", [id_or_paper_id, money_id]).fetchall()
        else:
            ret = self._sqlite_connection.execute_select("select * from points where id = ?", [id_or_paper_id]).fetchall()
        return (len(ret) > 0 and ret[0] or None)

    @raise_db_closed
    @in_transaction
    def remove_point(self, id_or_paper_id, money_id = None):
        """Removes point of this paper / money or by id
        Arguments:
        - `id_or_paper_id`:
        - `money_id`:
        """
        if money_id != None:
            self._sqlite_connection.execute("delete from points where paper_id = ? and money_id = ?", [id_or_paper_id, money_id])
        else:
            self._sqlite_connection.execute("delete from points where id = ?", [id_or_paper_id])

    @raise_db_closed
    @in_transaction
    def create_account(self, name, money_id_or_name, money_count, comment = None):
        """Creates a new account
        Arguments:
        - `name`:
        - `money_id_or_name`:
        - `money_count`:
        - `comment`:
        """
        if isinstance(money_id_or_name, basestring):
            mid = gethash(self.get_money(money_id_or_name), "id")
            if mid == None:
                raise od_exception("There is no such money {0}".format(money_id_or_name))
        else:
            mid = money_id_or_name
        return self._sqlite_connection.insert("accounts", {"name" : name, "comments" : comment, "money_id" : mid, "money_count" : money_count}).lastrowid

    @raise_db_closed
    def list_accounts(self, order_by = []):
        """Return list of accounts
        """
        return self._sqlite_connection.execute_select("select * from accounts{0}".format(order_by_print(order_by)))

    @raise_db_closed
    @remover_decorator("accounts", {int : "id", basestring : "name"})
    def remove_account(self, name_or_id):
        """Removes account by name or by id
        Arguments:
        - `name_or_id`:
        """
        pass

            
    @raise_db_closed
    @in_transaction
    def create_deal(self, account_id, deal):
        """creates one or more deal with attributes, return id of deal if creates one
        Arguments:
        - `account_id`:
        - `deal`: list of or one hash table with deal
        """
        for dd in (isinstance(deal, dict) and [deal] or deal):
            uat = gethash(dd, "user_attributes")
            if uat == None:
                uat = {}
                
