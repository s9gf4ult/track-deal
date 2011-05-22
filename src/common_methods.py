#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from math import *
import traceback
from exceptions import *
import datetime


def show_error(message, parent):
    win = parent
    dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
    dial.props.text = message
    dial.run()
    dial.destroy()

def find_in_list(findfunc, flist):
    for x in xrange(0, len(flist)):
        if findfunc(flist[x]):
            return x
    return None

def gethash(fhash, key):
    if fhash.has_key(key):
        return fhash[key]
    else:
        return None

def find_in_model(tmodel, findfunc):
    """returns path of found row in model"""
    it = tmodel.get_iter_first()
    while it != None:
        if findfunc(tmodel, it):
            return it
        it = tmodel.iter_next(it)
    return None

def is_null_or_empty(obj):
    return obj == None or len(obj) == 0

def reduce_by_string(reductor, seq):
    if len(seq) > 0:
        return reduce(lambda a, b: u'{0}{1}{2}'.format(a, reductor, b),
                      seq)
    else:
        return ""

def seconds_to_time_distance(seconds):
    ret = {}
    for (key, mlt) in [("days", 24 * 3600),
                       ("hours", 3600),
                       ("minutes", 60),
                       ("seconds", 1)]:
        ret[key] = trunc(seconds / mlt)
        seconds = seconds % mlt
    return ret

def time_distance_to_seconds(tdist):
    ret = reduce(lambda a, b: a + b,
                 map(lambda x, y: x * y,
                     [24 * 3600, 3600, 60, 1],
                     map(lambda k: gethash(tdist, k) != None and tdist[k] or 0,
                         ["days", "hours", "minutes", "seconds"])))
    return ret

def solve_lower_upper(plus, conds, field_name, l, h):
    if l and h:
        if l < h:
            conds.append(u'({0} between ? and ?)'.format(field_name))
            plus += [l, h]
        elif l > h:
            conds.append(u'({0} >= ? or {0} <= ?)'.format(field_name))
            plus += [l, h]
        else:
            conds.append(u'{0} = ?'.format(field_name))
            plus.append(l)
    elif l:
        conds.append(u'{0} >= ?'.format(field_name))
        plus.append(l)
    elif h:
        conds.append(u'{0} <= ?'.format(field_name))
        plus.append(h)

def show_and_print_error(error, window):
    show_error(error.__str__(), window)
    print(traceback.format_exc())

def no_reaction(func):
    """decorator which blocks an execution of the method of object which has `react` member, if react is False methid will not executed, before execution of the method `react` sets to False"""
    def ret(*args, **kargs):
        if not args[0].__do_react__:
            return
        try:
            args[0].__do_react__ = False
            func(*args, **kargs)
        finally:
            args[0].__do_react__ = True
    return ret

def if_database(func):
    """decorated method will be executed if self.database.connection != None"""
    def ret(*args, **kargs):
        if args[0].database.connection != None:
            func(*args, **kargs)
    return ret

def raise_db_closed(func):
    """Decorator makes function to raise Exception when
    self._sqlite_connection is null
    Arguments:
    - `func`:
    """
    def ret(*args, **kargs):
        rtt = None
        if hasattr(args[0], "_sqlite_connection"):
            if args[0]._sqlite_connection != None:
                rtt = func(*args, **kargs)
            else:
                raise od_exception_db_opened("Database is not opened now")
        else:
            raise od_exception("self has no attribute _sqlite_connection")
        return rtt
    ret.__doc__ = func.__doc__
    return ret

    
def raise_db_opened(func):
    """Decorator raises exception of databse is still opened
    Arguments:
    - `func`:
    """
    def ret(*args, **kargs):
        rtt = None
        if hasattr(args[0], "_sqlite_connection"):
            if args[0]._sqlite_connection == None:
                rtt = func(*args, **kargs)
            else:
                raise od_exception_db_opened("The database is still opened")
        else:
            raise od_exception("self has no attribute _sqlite_connection")
        return rtt
    ret.__doc__ = func.__doc__
    return ret

def in_transaction(func):
    """
    Decorator makes method executing in transaction, if error occures then transaction will be rolled back
    and exception will be passed up
    Arguments:
    - `func`:
    """
    def ret(*args, **kargs):
        self = args[0]
        self.begin_transaction()
        rtt = None
        try:
            rtt = func(*args, **kargs)
        except Exception as e:
            self.rollback()
            raise e
        else:
            self.commit()
        return rtt
    ret.__doc__ = func.__doc__
    return ret

class remover_decorator(object):
    """Makes method remove objects
    Attributes:
    
    """
    def __init__(self, table_name, class_field):
        """
        Arguments:
        - `table_name`: string with name of table delete entries from
        - `class_field`: hash like {argument_type: table field}
        """
        self._table_name = table_name
        self._class_field = class_field

    def __call__(self, method):
        """
        Arguments:
        - `method`:
        """
        def ret(*args, **kargs):
            rtt = method(*args, **kargs)
            farg = (isinstance(args[1], (list, tuple)) and args[1] or [args[1]])
            farg = map(lambda a: (a, ), farg)
            for classes in self._class_field.keys():
                if isinstance(farg[0][0], classes):
                    args[0]._sqlite_connection.executemany("delete from {0} where {1} = ?".format(self._table_name, self._class_field[classes]), farg)
                    break
            return rtt
        ret.__doc__ = method.__doc__
        return ret
        

def order_by_print(order_list = []):
    """generates string with `order by` definition
    Arguments:
    - `order_list`:
    """
    if len(order_list) > 0:
        return " order by {0}".format(reduce_by_string(", ", order_list))
    else:
        return ""

def remhash(hasht, key):
    """removes key from hashtable if exits
    Arguments:
    - `hasht`:
    - `key`:
    """
    if hasht.has_key(key):
        del hasht[key]

def format_where_part(wherepart, reductor = "and"):
    """return tuple of text for query and arguments for query
    Arguments:
    - `wherepart`: [(= | < | > | ... | 'between', [field_name], exp2, exp3 ...)]
    - `reductor`: `and` or `or` word for condition
    """
    exprlist = []
    arglist = []
    def formatarg(arg):
        if isinstance(arg, (tuple, list)):
            return arg[0]
        else:
            arglist.append(arg)
            return "?"
        
    def mkel():
        exprlist.append("{0} {1} {2}".format(formatarg(cond[1]), cond[0], formatarg(cond[2])))
        
    for cond in wherepart:
        assert(isinstance(cond, tuple))
        if cond[0] == 'between':
            exprlist.append("{0} between {1} and {2}".format(formatarg(cond[1]), formatarg(cond[2]), formatarg(cond[3])))
        elif cond[0] == "=" or cond[0] == "==":
            if isinstance(cond[1], (list, tuple)) and cond[2] == None:
                exprlist.append("{0} is null".format(cond[1][0]))
            elif isinstance(cond[2], (list, tuple)) and cond[1] == None:
                exprlist.append("{0} is null".format(cond[2][0]))
            else:
                mkel()
        elif cond[0] == "<>" or cond[0] == "!=":
            if isinstance(cond[1], (list, tuple)) and cond[2] == None:
                exprlist.append("{0} is not null".format(cond[1][0]))
            elif isinstance(cond[2], (list, tuple)) and cond[1] == None:
                exprlist.append("{0} is not null".format(cond[2][0]))
            else:
                mkel()
        else:
            mkel()
    return (reduce_by_string(" {0} ".format(reductor), exprlist), arglist)

def format_select_part(select_part):
    """return string with select part
    
    Arguments:
    - `select_part`: [* | field name | expression | (field name | expression, alias)]
    """
    rlist = []
    for sp in select_part:
        if isinstance(sp, basestring):
            rlist.append(sp)
        else:
            rlist.append("{0} as {1}".format(sp[0], sp[1]))
    return reduce_by_string(", ", rlist)
            
class safe_executeion(object):
    """Decorator executes given method if given attribute of the class is True
    and set this attribute to False after that, in any way decorated method will be executed
    """
    def __init__(self, attribute, method):
        """
        """
        self._attribute = attribute
        self._method = method

    def __call__(self, func):
        """
        Arguments:
        - `func`:
        """
        def ret(*args, **kargs):
            assert(hasattr(args[0], self._attribute))
            if getattr(args[0], self._attribute):
                self._method(*args, **kargs)
                setattr(args[0], self._attribute, False)
            return func(*args, **kargs)
        ret.__doc__ = func.__doc__
        return ret
    
class makes_insafe(object):
    """Decorator set attribute of object to true after the correct execution of decorated method
    """
    def __init__(self, attribute):
        """
        Arguments:
        - `attribute`:
        """
        self._attribute = attribute
        
    def __call__(self, func):
        """
        Arguments:
        - `func`:
        """
        def ret(*args, **kargs):
            rtt = None
            assert(hasattr(args[0], self._attribute))
            try:
                rtt = func(*args, **kargs)
            except e:
                raise e
            else:
                setattr(args[0], self._attribute, True)
            return rtt
        ret.__doc__ = func.__doc__
        return ret

def add_hash(h1, h2):
    """adds and replaces keys and vals of h2 to h1
    Arguments:
    - `h1`:
    - `h2`:
    """
    for k in h2.keys():
        h1[k] = h2[k]

def any_to_time(seconds):
    """turn seconds to time
    Arguments:
    - `seconds`:
    """
    seconds = int(seconds)
    h = trunc(seconds / 3600)
    seconds = seconds % 3600
    m = trunc(seconds / 60)
    seconds = seconds % 60
    s = trunc(seconds)
    return datetime.time(h, m, s)

def argument_value(name, value):
    """return string in format "name = value"
    Arguments:
    - `name`:
    - `value`:
    """
    if name != None:
        if value != None:
            return "{0} = {1}".format(name, value)
        else:
            return "{0}".format(name)
    else:
        return None

class string_reduce(object):
    """class for sqlite aggregate
    return string of splited by comma
    """
    _ret = ""
    def step(self, argument):
        """
        Arguments:
        - `argument`:
        """
        if not is_null_or_empty(argument):
            if is_null_or_empty(self._ret):
                self._ret = argument
            else:
                self._ret = "{0}, {1}".format(self._ret, argument)

    def finalize(self, ):
        """
        """
        return self._ret
    


def any_to_datetime(value):
    """return datetime
    Arguments:
    - `value`: any type convertable to float
    """
    return datetime.datetime.fromtimestamp(float(value))
