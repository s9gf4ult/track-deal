#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from math import trunc
import traceback
from od_exceptions import *
import datetime
import re
import sys

def show_error(message, parent):
    """
    \~russian
    \brief Отображает диалог в ошибкой
    \param message строка с описанием
    \param parent родительское окно диалога
    """
    win = parent
    dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
    dial.props.text = message
    dial.run()
    dial.destroy()

def find_in_list(findfunc, flist):
    """
    \~russian
    \brief поиск по списку
    \param функия поиска одного аргумента. Если функия вернет True - это означает что нужный элемент найден
    \param flist список (или кортеж) элементов
    \retval None не нашел ни одного элемента
    \retval integer индекс найденного элемента с 0
    """
    for x in xrange(0, len(flist)):
        if findfunc(flist[x]):
            return x
    return None

def format_number(value, max_after_comma = 2):
    """\brief format any number to pretty string with `max_after_comma` digits after comma or less
    \param value - number
    \param max_after_comma - int
    \return string
    """
    if value == round(value) and max_after_comma <> 0:
        return str(int(value))
    elif max_after_comma == 0:
        return str(int(round(value)))
    else:
        return str(round(value, max_after_comma))


def gethash(fhash, key):
    """
    \~russian
    \brief возвращает элемент хеш таблицы или None
    \param fhash таблица
    \param key ключ таблицы
    \retval None Нет такого элемента
    \retval Not-None значение \c fhash[key]
    \note Если значение \c fhash[key] == None то функция вернет None, нет возможности проверить
    наличия пары в хеш таблице при помощи этой функции
    """
    if fhash.has_key(key):
        return fhash[key]
    else:
        return None

def find_in_model(tmodel, findfunc):
    """\brief returns path of found row in model
    \param tmodel TreeModel instance
    \param findfunc function with two parameters:\n
    \c model TreeModel instance\n
    \c iterator TreeModelIter instance
    \retval None did not found
    \retval TreeModelIter instance - iterator on which function \c findfunc returned \c True
    """
    it = tmodel.get_iter_first()
    while it != None:
        if findfunc(tmodel, it):
            return it
        it = tmodel.iter_next(it)
    return None

def is_null_or_empty(obj):
    return obj == None or (hasattr(obj, "__len__") and len(obj) == 0)

def reduce_by_string(reductor, seq):
    """
    \~russian
    \param reductor строка будет вставлена между элементами seq
    \param seq список или кортеж элементов
    \return строка с элементами из \c seq между которыми \c reductor
    """
    if len(seq) > 0:
        return reduce(lambda a, b: u'{0}{1}{2}'.format(a, reductor, b),
                      seq)
    else:
        return ""

def seconds_to_time_distance(seconds):
    """
    \~russian
    \param seconds время в секундах
    \brief Переводит секунды во время
    \return Хеш таблица с ключами days, hours, minutes, seconds
    """
    ret = {}
    for (key, mlt) in [("days", 24 * 3600),
                       ("hours", 3600),
                       ("minutes", 60),
                       ("seconds", 1)]:
        ret[key] = trunc(seconds / mlt)
        seconds = seconds % mlt
    return ret

def time_distance_to_seconds(tdist):
    """
    \~russian
    \brief Переводит время в часах минутах секундах в секунды
    \param tdist хеш таблица с ключами days, hours, minutes, seconds
    \return integer соличество секунд
    """
    ret = reduce(lambda a, b: a + b,
                 map(lambda x, y: x * y,
                     [24 * 3600, 3600, 60, 1],
                     map(lambda k: gethash(tdist, k) != None and tdist[k] or 0,
                         ["days", "hours", "minutes", "seconds"])))
    return ret

def solve_lower_upper(plus, conds, field_name, l, h):
    """
    \~russian
    \brief вспомогательная функция для генерации запросов
    \param [out] plus список. Во время выполнения в него добавляются параметры запроса
    \param [out] conds список, во время выполнения в него добавляются условия запроса
    \param field_name имя поля участвующего в запросе
    \param l нижняя граница значения поля
    \param h верхняя граница значения поля
    """
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
    """
    \~russian
    \brief Показывает диалог с сообщением об ошибке и печатает стектрейс в stderr
    \param error объект ошибки
    \param window родительское окно для диалога
    """
    show_error(error.__str__(), window)
    sys.stderr.write(traceback.format_exc())

def no_reaction(func):
    """\~english \brief decorator

    which blocks an execution of the method of object which has `__do_react__` member, if __do_react__ is False methid will not executed, before execution of the method `__do_react__` sets to False
    \~russian
    \brief Декоратор

    Если атрибут __do_react__ объекта, чей метод декорируется, равен False - метод не выполняется, Если True выполняется при этом перед выполнением __do_react__ выставляется в False а после выполнения в True
    """
    def ret(*args, **kargs):
        if not args[0].__do_react__:
            return
        rtt = None
        try:
            args[0].__do_react__ = False
            rtt = func(*args, **kargs)
        finally:
            args[0].__do_react__ = True
        return rtt
    return ret

def if_database(func):
    """decorated method will be executed if self.database.connection != None
    \deprecated"""
    def ret(*args, **kargs):
        if args[0].database.connection != None:
            func(*args, **kargs)
    return ret

def raise_db_closed(func):
    """Decorator makes function to raise Exception when self._sqlite_connection is null
    \param func 
    """
    def ret(*args, **kargs):
        rtt = None
        if hasattr(args[0], "_sqlite_connection"):
            if args[0]._sqlite_connection != None:
                rtt = func(*args, **kargs)
            else:
                raise od_exception_db_closed("Database is not opened now")
        else:
            raise od_exception("self has no attribute _sqlite_connection")
        return rtt
    ret.__doc__ = func.__doc__
    return ret

    
def raise_db_opened(func):
    """Decorator raises exception of databse is still opened
    \param func 
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
    \~english
    Decorator makes method executing in transaction, if error occures then transaction will be rolled back
    and exception will be passed up
    \param func
    \~russian
    \brief Декоратор, выполняет метод в транзакции.

    Если во время выполнения метода возникает необработанное исключение - транзакция откатывается, в противном случае - commit.
    \param func декорируемый метод
    \note класс должен реализовывать методы \c begin_transaction, \c rollback и \c commit
    """
    def ret(*args, **kargs):
        self = args[0]
        self.begin_transaction()
        rtt = None
        try:
            rtt = func(*args, **kargs)
        except Exception as e:
            self.rollback()
            print(traceback.format_exc())
            raise e
        else:
            self.commit()
        return rtt
    ret.__doc__ = func.__doc__
    return ret

class remover_decorator(object):
    """
    \~english
    Makes method remove objects
    \~russian
    \brief Декоратор метода для удаления записей из базы.

    В конце метода выполняется код который удаляет записи из базы
    """
    def __init__(self, table_name, class_field):
        """
        \~english
        \param table_name  string with name of table delete entries from
        \param class_field  hash like {argument_type: table field}
        \~russian
        \param table_name имя таблицы из которой будут удалятся объекты
        \param class_field хеш таблица {тип_первого_аргумента : поле_в_таблице}\n
        Первый аргумент метода будет проверятся на соответствие типу \c тип_первого_аргумента,
        если тип совпадает, то значение аргумета будет сравнено со значением поля \c поле_в_таблице. То есть будет сгенерирован
        такой запрос\n
        \verbatim
        delete from table_name where поле_в_таблице = первый_аргумент
        \endverbatim
        Все это нужно для того чтобы можно было удалять обекты по id, и например по уникальному имени, которое является строкой
        """
        self._table_name = table_name
        self._class_field = class_field

    def __call__(self, method):
        """
        \param method 
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
    \param order_list
    \retval "" if order_list is empty
    """
    if len(order_list) > 0:
        return " order by {0}".format(reduce_by_string(", ", order_list))
    else:
        return ""

def remhash(hasht, key):
    """\brief removes key from hashtable if exits
    \param hasht 
    \param key 
    """
    if hasht.has_key(key):
        del hasht[key]

def format_where_part(wherepart, reductor = "and"):
    """return tuple of text for query and arguments for query
    \param wherepart  [(= | < | > | ... | 'between', [field_name], exp2, exp3 ...)]
    \param reductor  `and` or `or` word for condition
    \return (str, list)
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
    \param select_part  [* | field name | expression | (field name | expression, alias)]
    \return str
    """
    rlist = []
    for sp in select_part:
        if isinstance(sp, basestring):
            rlist.append(sp)
        else:
            rlist.append("{0} as {1}".format(sp[0], sp[1]))
    return reduce_by_string(", ", rlist)
            
class safe_execution(object):
    """Decorator executes given method if given attribute of the class is True
    and set this attribute to False after that, in any way decorated method will be executed
    \deprecated this is not usable anymore
    """
    def __init__(self, method, *attributes):
        """
        """
        self._attrbutes = attributes
        self._method = method

    def __call__(self, func):
        """
        \param func 
        """
        def ret(*args, **kargs):
            for attr in self._attrbutes:
                if args[0].get_database_attribute(attr) != None:
                    self._method(*args, **kargs)
                    break
            return func(*args, **kargs)
        ret.__doc__ = func.__doc__
        return ret
    
class makes_insafe(object):
    """Decorator set attribute of object to true after the correct execution of decorated method
    \deprecated
    """
    def __init__(self, attribute):
        """
        \param attribute 
        """
        self._attribute = attribute
        
    def __call__(self, func):
        """
        \param func 
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
    \param [out] h1 table to add pairs in
    \param h2 
    """
    for k in h2.keys():
        h1[k] = h2[k]

def any_to_time(seconds):
    """turn seconds to time
    \param seconds
    \return datetime.time instance
    """
    seconds = int(seconds)
    h = trunc(seconds / 3600)
    seconds = seconds % 3600
    m = trunc(seconds / 60)
    seconds = seconds % 60
    s = trunc(seconds)
    return datetime.time(h, m, s)

def argument_value(name, value):
    """return string in format "name = value" or just "name" if value == None
    \param name 
    \param value
    \return str
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
    \~russian
    \brief SQlite агрегатор, разделяет запятой все объекты и возвращает строку
    """
    _ret = ""
    def step(self, argument):
        """
        \param argument 
        """
        if not is_null_or_empty(argument):
            if is_null_or_empty(self._ret):
                self._ret = argument
            else:
                self._ret = "{0}, {1}".format(self._ret, argument)

    def finalize(self, ):
        return self._ret
    


def any_to_datetime(value):
    """return datetime
    \param value  any type convertable to float
    \return datetime.datetime instance
    """
    return datetime.datetime.fromtimestamp(float(value))

def any_to_date(value):
    """turn value to date
    \param value 
    """
    return datetime.date.fromtimestamp(float(value))

class in_action(object):
    """Decorator makes method executing in action
    \~russian
    \brief Декоратор исполняет метод внутри "действия"
    
    Создает "действие" в специальной таблице действий, если метод отрабатывает без ошибок
    действие завершается
    \note класс должен реализовывать \c start_action и \c end_action
    """
    def __init__(self, action_name):
        """
        \param action_name 
        """
        self._action_name = action_name
        
    def __call__(self, method):
        """
        \param method 
        """
        def ret(*args, **kargs):
            rtt = None
            try:
                args[0].start_action(self._action_name(*args, **kargs))
                rtt = method(*args, **kargs)
            finally:
                args[0].end_action()
            return rtt
        ret.__doc__ = method.__doc__
        return ret
    
class confirm_safety(object):
    """Decorator set database attributes to false after execution of method
    \deprecated
    """
    def __init__(self, *attributes):
        """
        \param *attributes 
        """
        self._attributes = attributes
        
    def __call__(self, method):
        """
        \param method 
        """
        def ret(*args, **kargs):
            rtt = method(*args, **kargs)
            args[0].remove_database_attribute(self._attributes)
            return rtt
        ret.__doc__ = method.__doc__
        return ret

class pass_to_method(object):
    """
    \~english
    Decorator call `method` after the body of decorated method and return value of `method`
    \~russian
    \brief Декоратор, вызывает метод - аргумет после декорируемого метода и возвращает то, что вернул метод аргумент

    Используется для передачи параметров другому методу, удобно для создания декорированных методов - оберток.
    Реализация самого декорируемого метода при этом можно опустить, или добавить некоторые действия, которые будут выполнены
    перед основным рабочим методом
    """
    def __init__(self, method):
        """
        \param method  method to call after decorated, and return value of
        """
        self._method = method

    def __call__(self, func):
        """
        \param func decorated method
        """
        def ret(*args, **kargs):
            func(*args, **kargs)
            return self._method(*args, **kargs)
        ret.__doc__ = func.__doc__
        return ret

def any_to_timedelta(value):
    """
    return timedelta from anything convertable to int
    \param value
    \return datetime.timedelta
    """
    return datetime.timedelta(0, int(value))

def format_abs_value(val):
    return (val < 0 and "({0})" or "{0}").format(format_number(abs(val)))


def is_blank(value):
    """\brief check if string consists of blank simbols or empty
    \param value string to check
    \retval True string does not contain not blank simbols or empty
    \retval False string has not blank simbols
    """
    if re.search("\S", value) == None:
        return True
    else:
        return False

def query_yes_no(query, window):
    """\brief ask the query in dialog
    \param query str with query
    \param window parent window for dialog
    \retval gtk.RESPONSE_YES
    \retval gtk.RESPONSE_NO
    """
    dial = gtk.MessageDialog(parent = window, flags = gtk.DIALOG_MODAL, type = gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO, message_format = query)
    ret = dial.run()
    dial.destroy()
    return ret

def query_yes_no_cancel(query, window):
    """\brief ask the query in dialog
    \param query str with query
    \param window parent window for dialog
    \retval gtk.RESPONSE_YES
    \retval gtk.RESPONSE_NO
    \retval gtk.RESPONSE_CANCEL
    """
    dial = gtk.Dialog()
    dial.get_content_area().pack_start(gtk.Label(query))
    dial.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    ret = dial.run()
    dial.destroy()
    return ret


def solve_field_in(args, conds, field_name, values):
    """\brief generate query for check if \c field_name in one of \c values
    \param args [out] - list of objects, will be appended by arguments
    \param conds [out] - list of string, will be appended by condition
    \param field_name - string, name of the field
    \param values - list of objects to append to arguments list
    """
    if not is_null_or_empty(values):
        q = "{0} in ({1})".format(field_name, reduce_by_string(", ", map(lambda a: "?", values)))
        conds.append(q)
        args.extend(values)

def make_builder(file_path):
    """\brief create and load gtk.Builder
    \param file_path - str, path to UI definition file
    """
    ret = gtk.Builder()
    ret.add_from_file(file_path)
    return ret
