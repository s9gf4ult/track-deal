#!/bin/env python
# -*- coding: utf-8 -*-
## sqlite_model ##

from common_model import common_model
from common_view import common_view
from sconnection import sconnection
import sources
from common_methods import raise_db_closed, raise_db_opened, remover_decorator, in_transaction, in_action, pass_to_method, reduce_by_string, remhash, gethash, any_to_datetime, format_abs_value, order_by_print, is_null_or_empty
from od_exceptions import od_exception_report_error, od_exception_parameter_error, od_exception_db_integrity_error, od_exception_action_cannot_create, od_exception_action_does_not_exists, od_exception_db_error, od_exception
from copy import copy
from datetime import datetime, date, timedelta
import sqlite3
import traceback
import sys
import os

class sqlite_model(common_model):
    """
    stores data in sqlite
    \~russian
    \todo сделать склейку сделок в случае удаления поз
    """
    ##############
    # Attributes #
    ##############
    ## file name or :memory:
    _connection_string = None
    ## \ref sconnection.sconnection instance
    _sqlite_connection = None
    
    ###########
    # Methods #
    ###########
    
    def __init__(self, ):
        """new instance of sqlite_model
        """
        pass

    def get_connection_string(self, ):
        """\brief return path to the file with database
        """
        return self._connection_string

    def get_paper_type(self, name_or_id):
        """\brief return paper_type object by name or id
        \param name_or_id - int or str
        """
        if isinstance(name_or_id, basestring):
            return self._sqlite_connection.execute_select('select * from paper_types where name = ?', [name_or_id]).fetchone()
        elif isinstance(name_or_id, int):
            return self._sqlite_connection.execute_select('select * from paper_types where id = ?', [name_or_id]).fetchone()
        else:
            raise od_exception_parameter_error('name_or_id must be int or str not {0}'.format(type(name_or_id)))

    def create_paper_type(self, name, comment = ''):
        """\brief create new paper type
        \param name - str
        \param comment - str
        \return int - id of new paper type
        \note view must use \ref tacreate_paper_type instead
        """
        try:
            return self._sqlite_connection.insert('paper_types', {'name' : name,
                                                                  'comment' : comment})
        except sqlite3.IntegrityError as e:
            raise od_exception_db_integrity_error(str(e))
        except sqlite3.OperationalError as e:
            raise od_exception_db_error(str(e))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: u'create paper type {0}'.format(name))
    @pass_to_method(create_paper_type)
    def tacreate_paper_type(self, *args, **kargs):
        """\brief wrapper around \ref create_paper_type
        \param name - str
        \param comment - str
        """
        pass


    @remover_decorator('paper_types', {int: 'id', basestring : 'name'})
    def remove_paper_type(self, id_or_name):
        """\brief remove paper by name or by id
        \param id_or_name
        \note view must use \ref taremove_paper_type instead
        """
        pass

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, id_or_name, *args, **kargs: 'remove paper type {0}'.format(id_or_name))
    @pass_to_method(remove_paper_type)
    def taremove_paper_type(self, *args, **kargs):
        """\brief wrapper around \ref remove_paper_type
        \param id_or_name
        """
        pass

    def list_paper_types(self, order_by = ['name']):
        """\brief return iteration object to receive paper types
        \param order_by
        """
        return self._sqlite_connection.execute_select('select * from paper_types{0}'.format(order_by_print(order_by)))


    @raise_db_opened
    def connect(self, connection_string):
        """connects to file or memory
        
        \param connection_string 
        """
        assert(isinstance(connection_string, basestring))
        self._connection_string = connection_string
        self._sqlite_connection = sconnection(connection_string)

    def connected(self, ):
        """return true if connected
        """
        return self._sqlite_connection <> None


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
        \param filename 
        """
        if os.path.exists(filename):
            self.connect(filename)
            self.dbtemp()
            self.recalculate_all_temporary()
        else:
            raise od_exception('There is no such file {0}'.format(filename))

    @raise_db_opened
    def create_new(self, filename):
        """Creates new empty database
        \param filename 
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

    def commit(self, ):
        """Commits
        """
        self._sqlite_connection.commit()

    def rollback(self, ):
        """Rollback
        """
        self._sqlite_connection.rollback()

    def add_global_data(self, parameters):
        """adds global data and
        \param parameters  hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("global_data", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names)))

    def select_account(self, account_id):
        """set the current account in the database
        \param account_id 
        """
        self._sqlite_connection.insert("global_data", {"name" : "current_account", "value" : account_id})

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account_id: "set {0} as current account".format(account_id))
    @pass_to_method(select_account)
    def taselect_account(self, account_id):
        """wrapper for select account
        \param account_id 
        """
        pass


    @raise_db_closed
    @in_transaction
    @in_action(lambda self, parameters: "add parameters {0}".format(reduce_by_string(", ", paramters.keys())))
    @pass_to_method(add_global_data)
    def taadd_global_data(self, paramters):
        """
        \param paramters 
        """
        pass

    def get_global_data(self, name):
        """returns value of global data or None if there is no one
        \param name
        \retval value of param
        \retval None if not exists parameter with this name
        """
        ret = self._sqlite_connection.execute_select("select value from global_data where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

        

    def remove_global_data(self, name):
        """Removes global parameters
        \param name string or list of strings to remove global data
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from global_data where name = ?", name)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: "remove global data {0}".format(reduce_by_string(", ", (isinstance(name, basestring) and [name] or name))))
    @pass_to_method(remove_global_data)
    def taremove_global_data(self, name):
        """
        \param name string or list of strings to remove global data
        """
        pass

    def list_global_data(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from global_data"))

    def add_database_attributes(self, parameters):
        """adds database attributes and
        \param parameters  hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("database_attributes", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names)))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, paramters, *args, **kargs: "add database attributes {0}".format(reduce_by_string(", ", parameter.keys())))
    @pass_to_method(add_database_attributes)
    def taadd_database_attributes(self, paramters):
        """
        """
        pass

    def get_database_attribute(self, name):
        """returns value of global parameter or None if there is no one
        \param name 
        """
        ret = self._sqlite_connection.execute_select("select value from database_attributes where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

    def remove_database_attribute(self, name):
        """Removes global parameters
        \param name  string or list of strings to remove
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from database_attributes where name = ?", name)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: "remove database attributes {0}".format(reduce_by_string(", ", (isinstance(name, basestring) and [name] or name))))
    @pass_to_method(remove_database_attribute)
    def taremove_database_attribute(self, name):
        """
        \param name 
        """
        pass

    def list_database_attributes(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from database_attributes"))
    
    def create_paper(self, type, name, stock = None, class_name = None, full_name = None):
        """creates new paper and returns it's id
        
        \param type - int or str, if str - then type is name field of paper_types table else is id
        \param name - str
        \param stock - str
        \param class_name - str
        \param full_name - str
        """
        try:
            t = self.get_paper_type(type)
            if t == None:
                raise od_exception_parameter_error('There is no such paper type {0}'.format(type))
            return self._sqlite_connection.insert("papers", {"type" : t['id'],
                                                             "stock" : stock,
                                                             "class" : class_name,
                                                             "name" : name,
                                                             "full_name" : full_name})
        except sqlite3.IntegrityError as e:
            raise od_exception_db_integrity_error(str(e))
        except sqlite3.OperationalError as e:
            raise od_exception_db_integrity_error(str(e))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, type, name, *args, **kargs: "create paper type {0}, name {1}".format(type, name))
    @pass_to_method(create_paper)
    def tacreate_paper(self, *args, **kargs):
        """
        \param type 
        \param name 
        \param stock 
        \param class_name 
        \param full_name 
        """
        pass



    def get_paper(self, type_or_id, name = None):
        """returns paper by name or by id
        if there is no one returns None
        \param type_or_id 
        """
        if name == None:
            if isinstance(type_or_id, int):
                try:
                    return self._sqlite_connection.execute_select('select * from papers where id = ?', [type_or_id]).fetchone()
                except sqlite3.IntegrityError as e:
                    raise od_exception_db_integrity_error(str(e))
            else:
                raise od_exception_parameter_error('if name is None then type_or_id must be int not {0}'.format(type(type_or_id)))
        else:
            try:
                t = self.get_paper_type(type_or_id)
                if t == None:
                    raise od_exception_parameter_error('there is not such paper_type {0}'.format(type_or_id))
                return self._sqlite_connection.execute_select('select * from papers where type = ? and name = ?', [t['id'], name]).fetchone()
            except sqlite3.IntegrityError as e:
                return od_exception_db_integrity_error(str(e))

    @raise_db_closed
    def list_papers_view(self, order_by = ['name']):
        """\brief list papers joined with types
        \param order_by
        """
        return self._sqlite_connection.execute_select('select p.id as id, p.name as name, p.type as type, p.class as class, p.stock as stock, p.full_name as full_name, t.name as type_name, t.comment as type_comment from papers p inner join paper_types t on p.type = t.id{0}'.format(order_by_print(order_by)))

    def remove_paper(self, type_or_id, name = None):
        """Removes one paper by type and name or many papers by id
        
        \param type_or_id 
        \param name 
        """
        if name == None:
            if isinstance(type_or_id, int):
                self._sqlite_connection.execute('delete from papers where id = ?', [type_or_id])
            else:
                raise od_exception_parameter_error('if name is None then type_or_id must be int not {0}'.format(type(type_or_id)))
        else:
            try:
                t = self.get_paper_type(type_or_id)
                if t == None:
                    raise od_exception_parameter_error('There is no such paper type {0}'.format(type_or_id))
                self._sqlite_connection.execute('delete from papers where type = ? and name = ?', [t['id'], name])
            except sqlite3.IntegrityError as e:
                raise od_exception_db_integrity_error(str(e))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, torid, name = None: "remove paper {0}".format((isinstance(torid, int) and "with id {0}".format(torid) or "with type {0} and name {1}".format(torid, name))))
    @pass_to_method(remove_paper)
    def taremove_paper(self, *args, **kargs):
        """
        \param *args 
        \param **kargs 
        """
        pass


    def list_papers(self, order_by = []):
        """Returns list of papers
        \return hash table with keys:\n
        \c id - int, id of paper\n
        \c type - str, type of paper "stock", "option", "future" or so on\n
        \c stock - str, name of stock\n
        \c class - str, name of class if exists\n
        \c name - str, name of this paper\n
        \c full_name - str, full name or comment
        """
        q = "select * from papers{0}".format(order_by_print(order_by))
        return self._sqlite_connection.execute_select(q)
    

    def change_paper(self, paper_id, fields):
        """changes existing paper
        \param paper_id - int, id of paper object
        \param fields  hash {"field" : value}
        """
        if len(fields) > 0:
            if self._sqlite_connection.execute("select count(*) from papers where id = ?", [paper_id]).fetchone()[0] > 0:
                remhash(fields, "id")
                self._sqlite_connection.update("papers", fields, 'id = ?', (paper_id, ))
                for (aid, ) in self._sqlite_connection.execute("select distinct account_id from deals where paper_id = ?", [paper_id]):
                    self.recalculate_deals(aid)
                for (aid, ) in self._sqlite_connection.execute("select distinct account_id from positions where paper_id = ?", [paper_id]):
                    self.recalculate_positions(aid)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, paper_id, *args, **kargs: "change paper {0}".format(paper_id))
    @pass_to_method(change_paper)
    def tachange_paper(self, *args, **kargs):
        """
        \param paper_id 
        \param fields  hash {"field" : value}
        """
        pass


    def create_candles(self, paper_id, candles):
        """Creates one or several candles of paper `paper_id`
        \param paper_id 
        \param candles  hash table with keys, [duration, open_datetime, close_datetime, open_value, close_value, min_value, max_value, volume, value_type] or the list of tables
        """
        candles = (isinstance(candles, dict) and [candles] or candles)
        for candle in candles:
            candle["paper_id"] = paper_id
            assert(candle["min_value"] <= candle["open_value"] <= candle["max_value"])
            assert(candle["min_value"] <= candle["close_value"] <= candle["max_value"])
            assert(candle["open_datetime"] < candle["close_datetime"])
            assert(isinstance(candle["duration"], basestring,))
        self._sqlite_connection.insert("candles", candles)


    def get_candle(self, candle_id):
        """Get candle by id
        \param candle_id 
        """
        ret = self._sqlite_connection.execute_select("select * from candles where id = ?", [candle_id]).fetchall()
        return (len(ret) > 0 and ret[0] or None)

    @remover_decorator("candles", {int : "id"})
    def remove_candle(self, candles_id):
        """removes one or more candles
        \param candles_id  int or list of ints
        """
        pass

    def list_candles(self, paper_id, order_by = []):
        """Return ordered list of candles
        \param paper_id 
        \param order_by 
        """
        q = "select * from candles where paper_id = ?"
        if len(order_by) > 0:
            q += "order by {0}".format(reduce_by_string(", ", order_by))
        return self._sqlite_connection.execute_select(q, [paper_id])


    def create_money(self, name, full_name = None):
        """Creates new money and return it's id
        \param name 
        \param full_name
        \note in the view must be used \ref tacreate_money
        return id of the new created money object
        """
        return self._sqlite_connection.insert("moneys", {"name" : name,
                                                         "full_name" : full_name})
    
    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: "add money {0}".format(name))
    @pass_to_method(create_money)
    def tacreate_money(self, name, full_name = None):
        """transacted wrapper for \ref create_money
        \param name 
        \param full_name 
        """
        pass

    def create_money_list(self, money_list):
        """\brief create many money objects
        \param money_list list of hashes with keys "name" and "full_name"
        \note view must use \ref tacreate_money_list insted
        """
        self._sqlite_connection.insert("moneys", money_list)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, mlist: "create {0} money objects".format(len(mlist)))
    @pass_to_method(create_money_list)
    def tacreate_money_list(self, *args, **kargs):
        """\brief wrapper around \ref create_money_list 
        \param money_list list of hashes with keys "name" and "full_name"
        """
        pass



    def get_money(self, name_or_id):
        """Returns money object by id or name
        \param name_or_id 
        """
        if isinstance(name_or_id, basestring):
            ret = self._sqlite_connection.execute_select("select * from moneys where name = ?", [name_or_id]).fetchall()
        elif isinstance(name_or_id, int):
            ret = self._sqlite_connection.execute_select("select * from moneys where id = ?", [name_or_id]).fetchall()
        else:
            raise od_exception("get_money: incorrect parameters")
        
        return (len(ret) > 0 and ret[0] or None)

    @remover_decorator("moneys", {int : "id", basestring : "name"})
    def remove_money(self, name_or_id):
        """Removes money by name or by id
        \param name_or_id
        \note assigned accounts will be removed automatically by constraint
        """
        pass

    def assigned_to_money_accounts(self, name_or_id):
        """\brief return count fo accounts assigned to money
        \param name_or_id name or id of money object
        \return int - count
        \exception od_exception_db_error if there is no such money
        """
        mm = self.get_money(name_or_id)
        if mm == None:
            raise od_exception_db_error("There is no moneys \"{0}\"".format(name_or_id))
        (c,) = self._sqlite_connection.execute("select count(a.id) from accounts a inner join moneys m on a.money_id = m.id where m.id = ?", [mm["id"]]).fetchone()
        return c

    def start_transacted_action(self, action_name):
        """\brief start transaction and action
        \param action_name
        \note action must be commited by \ref commit_transacted_action or rolled back by \ref rollback
        """
        self.begin_transaction()
        self.start_action(action_name)

    def commit_transacted_action(self, ):
        """\brief finish action and commit
        """
        self.end_action()
        self.commit()

    def list_moneys(self, order_by = []):
        """return list of moneys
        \return list of hash tables with keys \c id, \c name, \c full_name
        """
        q = "select * from moneys{0}".format((len(order_by) > 0 and " order by {0}".format(reduce_by_string(", ", order_by))  or ""))
        return self._sqlite_connection.execute_select(q)
    
    def create_point(self, paper_id, money_id, point, step):
        """Creates point explanation and return it's id
        \param paper_id 
        \param money_id 
        \param point 
        \param step 
        """
        ret = self._sqlite_connection.insert("points", {"paper_id" : paper_id, "money_id" : money_id, "point" : point, "step" : step})
        for (aid, ) in self._sqlite_connection.execute("select id from accounts where money_id = ?", [money_id]):
            self.recalculate_deals(aid)
            self.recalculate_positions(aid)
        return ret

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, paper_id, money_id, *args, **kargs: "create point for paper {0} and money {1}".format(paper_id, money_id))
    @pass_to_method(create_point)
    def tacreate_point(self, *args, **kargs):
        """transacted wrapper for create point
        \param *args 
        \param **kargs 
        """
        pass

    
    def list_points(self, money_id = None, order_by = []):
        """Return list of points
        \param money_id 
        \param order_by 
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

    def get_point(self, id_or_paper_id, money_id = None):
        """Returns point explanation by id or by paper_id and money_id
        \param id_or_paper_id 
        \param money_id 
        """
        if money_id != None:
            ret = self._sqlite_connection.execute_select("select * from points where paper_id = ? and money_id = ?", [id_or_paper_id, money_id]).fetchall()
        else:
            ret = self._sqlite_connection.execute_select("select * from points where id = ?", [id_or_paper_id]).fetchall()
        return (len(ret) > 0 and ret[0] or None)

    def remove_point(self, id_or_paper_id, money_id = None):
        """Removes point of this paper / money or by id
        \param id_or_paper_id 
        \param money_id 
        """
        if money_id != None:
            self._sqlite_connection.execute("delete from points where paper_id = ? and money_id = ?", [id_or_paper_id, money_id])
            for (aid, ) in self._sqlite_connection.execute("select id from accounts where money_id = ?", [money_id]):
                self.recalculate_deals(aid)
                self.recalculate_positions(aid)
        else:
            self._sqlite_connection.execute("delete from points where id = ?", [id_or_paper_id])
            (paid, ) = self._sqlite_connection.execute("select paper_id from points where id = ?", [id_or_paper_id]).fetchone() or (None, )
            if paid <> None:
                for (aid, ) in self._sqlite_connection.execute("select a.id from accounts a inner join points p on p.money_id = a.money_id where p.id = ?", [id_or_paper_id]):
                    self.recalculate_deals(aid)
                    self.recalculate_positions(aid)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, id_or_paper_id, money_id = None:"remove point {0}".format((money_id == None and "with id {0}".format(id_or_paper_id) or "with paper_id {0} and money_id {1}".format(id_or_paper_id, money_id))))
    @pass_to_method(remove_point)
    def taremove_point(self, *args, **kargs):
        """transacted wrapper for remove point
        \param *args 
        \param **kargs 
        """
        pass




    def create_account(self, name, money_id_or_name, money_count, comment = None):
        """Creates a new account
        \param name 
        \param money_id_or_name 
        \param money_count 
        \param comment 
        """
        if isinstance(money_id_or_name, basestring):
            mid = gethash(self.get_money(money_id_or_name), "id")
            if mid == None:
                raise od_exception("There is no such money {0}".format(money_id_or_name))
        else:
            mid = money_id_or_name
        aid = self._sqlite_connection.insert("accounts", {"name" : name, "comments" : comment, "money_id" : mid, "money_count" : money_count})
        if self.get_global_data("current_account") == None and self._sqlite_connection.execute("select count(*) from accounts").fetchone()[0] == 1:
            self.add_global_data({"current_account" : aid})
        return aid

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: u"create account {0}".format(name))
    @pass_to_method(create_account)
    def tacreate_account(self, *args, **kargs):
        """transacted wrapper for create account
        \param name name of account
        \param money_id_or_name id or name of money assigned to account
        \param money_count initial monay amount
        \param comment optional comment
        \return integer as id of new created account
        \exception exceptions.od_exception money id or name does not exists in database
        \exception sqlite3.IntegrityError account with such name already exists
        """
        pass


    def change_account(self, aid, name = None, money_id_or_name = None, money_count = None, comment = None):
        """changes existing account
        \param aid - int
        \param name - str, new name or None
        \param money_id_or_name - int or str, new money or None 
        \param money_count - float, new initial money amount or None
        \param comment - str, new comment or None
        \note \ref tachange_account must be used by model instead
        """
        sets = {}
        if name != None:
            sets["name"] = name
        if money_id_or_name != None:
            m = self.get_money(money_id_or_name)
            sets["money_id"] = m["id"]
        if money_count != None:
            sets["money_count"] = money_count
        if comment != None:
            sets["comments"] = comment
        if len(sets) > 0:
            self._sqlite_connection.update("accounts", sets, "id = ?", (aid, ))

        if money_id_or_name <> None or money_count <> None:
            self.recalculate_deals(aid)
            self.recalculate_positions(aid)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, aid, *args, **kargs: "changed account with id {0}".format(aid))
    @pass_to_method(change_account)
    def tachange_account(self, *args, **kargs):
        """transacted wrapper for \ref change_account
        \param aid - int
        \param name - str, new name or None
        \param money_id_or_name - int or str, new money or None 
        \param money_count - float, new initial money amount or None
        \param comment - str, new comment or None
        """
        pass

    def list_accounts(self, order_by = []):
        """Return list of accounts
        """
        return self._sqlite_connection.execute_select_cond("accounts", order_by = order_by)

    @remover_decorator("accounts", {int : "id", basestring : "name"})
    def remove_account(self, name_or_id):
        """Removes account by name or by id and set current account to None deleted current
        \param name_or_id 
        """
        acc = self.get_account(name_or_id)
        cacc = self.get_current_account()
        if acc <> None and cacc <> None:
            if acc["id"] == cacc["id"]:
                self.set_current_account(None)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, name_or_id: "remove account with {0}".format((isinstance(name_or_id, int) and "id {0}".format(name_or_id) or "name {0}".format(name_or_id))))
    @pass_to_method(remove_account)
    def taremove_account(self, *args, **kargs):
        """transacted wrapper for remove account
        \param name_or_id name or id of account
        """
        pass


    def get_account(self, aid_or_name):
        """
        \param aid_or_name account id or account name
        \retval hash table with fields id, name, comments, money_id, money_count
        \retval None if no one account with this id or name
        \exception exceptions.od_exception when aid_or_name is not of type (str, int, long)
        """
        if (isinstance(aid_or_name, basestring)):
            return self._sqlite_connection.execute_select("select * from accounts where name = ?", [aid_or_name]).fetchone()
        elif (isinstance(aid_or_name, (int, long))):
            return self._sqlite_connection.execute_select("select * from accounts where id = ?", [aid_or_name]).fetchone()
        else:
            raise od_exception()

            
    def create_deal(self, account_id, deal, do_recalc = True):
        """creates one or more deal with attributes, return id of last created
        \param account_id 
        \param deal list of or one hash table with keys:\n
        sha1 - optional unique field\n
        manual_made - not None means deals inserted by hand\n
        parent_deal_id - id of parent deal (must not be used for new deals)\n
        account_id - this will be replaced by first parameter\n
        position_id - this will be calculated automatically\n
        paper_id - id of paper deal assigned to\n
        count - count of lots\n
        direction - (-1) means BY, 1 means SELL\n
        points - price in points\n
        commission - summarized commission\n
        datetime - datetime.datetime instance
        \param do_recalc if True recalculation of temporarry tables will be executed
        \return int - deal id
        \note \ref tacreate_deal must be used instead by the view
        """
        did = None
        deals = (isinstance(deal, dict) and [deal] or deal)
        paper_deal = None
        for dd in deals:
            dd = copy(dd)
            uat = gethash(dd, "user_attributes")
            if uat == None:
                uat = {}
            sat = gethash(dd, "stored_attributes")
            if sat == None:
                sat = {}
            remhash(dd, "user_attributes")
            remhash(dd, "stored_attributes")
            dd["account_id"] = account_id
            did = self._sqlite_connection.insert("deals", dd)
            if len(uat) > 0:
                uk = uat.keys()
                uv = map(lambda k: uat[k], uk)
                self._sqlite_connection.executemany("insert into user_deal_attributes(deal_id, name, value) values (?, ?, ?)", map(lambda name, value: (did, name, value), uk, uv)) 
            if len(sat) > 0:
                sk = sat.keys()
                sv = map(lambda k: sat[k], sk)
                self._sqlite_connection.executemany("insert into stored_deal_attributes(deal_id, type, value) values (?, ?, ?)", map(lambda typ, val: (did, typ, val), sk, sv))
            if do_recalc:
                if paper_deal == None or (paper_deal[1] > dd["datetime"]) or (paper_deal[1] == dd["datetime"] and paper_deal[0] > did):
                    paper_deal = (did, dd["datetime"])
        if do_recalc:
            self.recalculate_deals(account_id, paper_deal[0])
        return did

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account_id, deal, *args, **kargs: (isinstance(deal, (tuple, list)) and "create {0} deals".format(len(deal)) or "create deal with paper id {0}".format(deal["paper_id"])))
    @pass_to_method(create_deal)
    def tacreate_deal(self, *args, **kargs):
        """wrapper for \ref create_deal
        \param account_id 
        \param deal list of or one hash table with keys:\n
        sha1 - optional unique field\n
        manual_made - not None means deals inserted by hand\n
        parent_deal_id - id of parent deal (must not be used for new deals)\n
        account_id - this will be replaced by first parameter\n
        position_id - this will be calculated automatically\n
        paper_id - id of paper deal assigned to\n
        count - count of lots\n
        direction - (-1) means BY, 1 means SELL\n
        points - price in points\n
        commission - summarized commission\n
        datetime - datetime.datetime instance
        \return int - deal id
        \param do_recalc if True recalculation of temporarry tables will be executed
        """
        pass


    def list_deals(self, account_id = None, paper_id = None, order_by = []):
        """Return cursor iterating on deals
        \param account_id 
        \param paper_id 
        \param order_by 
        """
        conds = []
        if account_id != None:
            conds.append(("=", ["account_id"], account_id))
        if paper_id != None:
            conds.append(("=", ["paper_id"], paper_id))
        return self._sqlite_connection.execute_select_cond("deals", wheres = conds, order_by = order_by)
        
    def remove_deal(self, deal_id):
        """\brief remove one or more deal by id
        \param deal_id - int or list of int's
        \note \ref taremove_deal must be used insted
        """
        x = map(lambda a: (a, ), (isinstance(deal_id, int) and [deal_id] or deal_id))
        self._sqlite_connection.executemany("delete from deals where id = ?", x)
        self._sqlite_connection.executemany("delete from deals_view where deal_id = ?", x)
        self.fix_groups()
        self.fix_positions()

    def fix_groups(self, ):
        """\brief fixes broken groups by deleting
        \~russian

        Если в группе находятся не сбалансированное количество сделок или нет ни одной привязанной к группе сделки то группа удаляется
        \todo добавить удаление групп данные в ктороых не соответствуют данным в сделках
        """
        self._sqlite_connection.execute("""delete from deal_groups where id in (
        select id from (
        select g.group_id as id, count(d.id) as count
        from deal_group_assign g left join deals d on g.deal_id = d.id
        group by g.group_id)
        where count = 0

        union

        select g.id from deal_groups g
        where not exists(select * from deal_group_assign where group_id = g.id)

        union

        select id from (
        select g.group_id as id, sum(d.count * d.direction) as sum
        from deal_group_assign g left join deals d on g.deal_id = d.id
        group by g.group_id)
        where sum <> 0)""")

    def fix_positions(self, ):
        """\brief fixes broken positions by deleting
        \~russian

        Удаляются позиции по с не сбалансированным количеством сделок и/или позиции к которым не привязана ни одна позиция
        \todo добавить удаление позиций с некорректными данными (тоесть количество сбалансированное, но данные в позициях не соответствуют данным в сделках)
        """
        self._sqlite_connection.execute("""
        delete from positions where id in (
        select id from positions p
        where not exists(select * from deals where position_id = p.id)

        union

        select id from (
        select p.id as id, sum(d.count * d.direction) as sum
        from positions p inner join deals d on d.position_id = d.id
        group by p.id)
        where sum <> 0)""")

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, deal_id, *args, **kargs: "remove deals(s)".format(deal_id))
    @pass_to_method(remove_deal)
    def taremove_deal(self, *args, **kargs):
        """\brief wrapper around \ref remove_deal
        \param deal_id int or list of ints
        """
        pass

    def get_user_deal_attributes(self, deal_id):
        """return hash of attributes
        \param deal_id 
        """
        ret = {}
        for at in self._sqlite_connection.execute_select_cond("user_deal_attributes", wheres = [("=", ["deal_id"], deal_id)]):
            ret[at["name"]] = at["value"]
        return ret

    def get_stored_deal_attributes(self, deal_id):
        """return hash of stored attributes
        
        \param deal_id 
        """
        ret = {}
        for at in self._sqlite_connection.execute_select_cond("stored_deal_attributes", wheres = [("=", ["deal_id"], deal_id)]):
            ret[at["type"]] = at["value"]
        return ret

    def _create_position_raw(self, position, do_recalc = True):
        """just create position in database 
        \param position  hash table, keys may be "user_attributes", "stored_attributes", "deals_assigned" and fields of table positions. It can be list of this hashes
        """
        if is_null_or_empty(position):
            return
        pss = (isinstance(position, (list, tuple)) and position or [position])
        paper_position = None             # {paper_id : (position_id, close_datetime, open_datetime)}
        aid = None
        pid = None
        for ps in pss:
            xps = copy(ps)
            remhash(xps, "user_attributes")
            remhash(xps, "stored_attributes")
            remhash(xps, "deals_assigned")
            remhash(xps, "id")
            pid = self._sqlite_connection.insert("positions", xps)
            if isinstance(gethash(ps, "user_attributes"), dict):
                self._sqlite_connection.insert("user_position_attributes", map(lambda k: {"position_id" : pid, "name" : k, "value" : ps["user_attributes"][k]}, ps["user_attributes"].keys()))
            if isinstance(gethash(ps, "stored_attributes"), dict):
                self._sqlite_connection.insert("stored_position_attributes", map(lambda k: {"position_id" : pid, "type" : k, "value" : ps["stored_attributes"][k]}, ps["stored_attributes"].keys()))
            if gethash(ps, "deals_assigned") <> None:
                self._sqlite_connection.executemany("update deals set position_id = ? where id = ?", map(lambda a: (pid, a), ps["deals_assigned"]))
            if do_recalc:
                if paper_position == None or (paper_position[1] > ps["close_datetime"]) or (paper_position[1] == ps["close_datetime"] and (paper_position[2] > ps["open_datetime"] or (paper_position[2] == ps["open_datetime"] and paper_position[0] > pid))):
                    paper_position = (pid, ps["close_datetime"], ps["open_datetime"])
            aid = ps["account_id"]
            
        if do_recalc:
            self.recalculate_positions(aid, paper_position[0])
        return pid
                    
    def create_position_hash(self, open_group_id, close_group_id, user_attributes = {}, stored_attributes = {}, manual_made = None, do_not_delete = None):
        """return hash to insert by _create_position_raw
        \param open_group_id 
        \param close_group_id 
        \param user_attributes 
        \param stored_attributes 
        \param manual_made 
        \param do_not_delete 
        """
        for field in ["paper_id", "account_id"]:
            odids = self._sqlite_connection.execute("select count(*) from (select distinct d.{0} from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on dg.group_id = g.id where g.id = ? or g.id = ?)".format(field), [open_group_id, close_group_id]).fetchone()[0]
            assert(odids == 1)

        odirs = map(lambda a: self._sqlite_connection.execute("select distinct d.direction from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ?", [a]).fetchall(), [open_group_id, close_group_id])
        assert(len(odirs[0]) == len(odirs[1]) == 1)
        assert(odirs[0][0][0] == -(odirs[1][0][0]) <> 0)
        cnts = map(lambda a: self._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [a]).fetchone()[0], [open_group_id, close_group_id])
        assert(cnts[0] == cnts[1])
        assert(cnts[0] > 0)
               
        dds = self._sqlite_connection.execute("select max(d.datetime), min(dd.datetime) from deals d inner join deal_group_assign dg on dg.deal_id = d.id, deals dd inner join deal_group_assign ddg on ddg.deal_id = dd.id where dg.group_id = ? and ddg.group_id = ?", [open_group_id, close_group_id]).fetchone()
        assert(dds[0] <= dds[1])
        (apids, ) = self._sqlite_connection.execute("select count(*) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where (dg.group_id = ? or dg.group_id = ?) and d.position_id is not null", [open_group_id, close_group_id]).fetchone()
        assert(apids == 0)
        (acc_id, pap_id) = self._sqlite_connection.execute("select d.account_id, d.paper_id from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? limit 1", [open_group_id]).fetchone()
        (comm, ) = self._sqlite_connection.execute("select sum(d.commission) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? or dg.group_id = ?", [open_group_id, close_group_id]).fetchone()
        (odate, opoints) = self._sqlite_connection.execute("select max(d.datetime), sum(d.points * d.count) / sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [open_group_id]).fetchone()
        (cdate, cpoints) = self._sqlite_connection.execute("select max(d.datetime), sum(d.points * d.count) / sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [close_group_id]).fetchone()        

        ret = {"account_id" : acc_id,
               "paper_id" : pap_id,
               "count" : cnts[0],
               "direction" : odirs[0][0][0],
               "commission" : comm,
               "open_datetime" : odate,
               "close_datetime" : cdate,
               "open_points" : opoints,
               "close_points" : cpoints,
               "manual_made" : manual_made,
               "do_not_delete" : do_not_delete}
        if len(stored_attributes) > 0:
            ret["stored_attributes"] = stored_attributes
        if len(user_attributes) > 0:
            ret["user_attributes"] = user_attributes
        dds = self._sqlite_connection.execute("select distinct deal_id from deal_group_assign where group_id = ? or group_id = ?", [open_group_id, close_group_id]).fetchall()
        if len(dds) > 0:
            ret["deals_assigned"] = map(lambda a: a[0], dds)
        return ret



            

    def create_position(self, open_group_id, close_group_id, user_attributes = {}, stored_attributes = {}, manual_made = None, do_not_delete = None):
        """Return position id built from groups
        \param open_group_id 
        \param close_group_id 
        """
        pid = self._create_position_raw(self.create_position_hash(open_group_id, close_group_id, user_attributes, stored_attributes, manual_made, do_not_delete))
        return pid

    def create_position_from_data(self, account_id_or_name, data):
        """\brief create position object and proper deal objects
        \param account_id_or_name - int or string
        \param data - hash table with keys:\n
        \c paper_id - int, id of paper object\n
        \c count - int, count of contracts\n
        \c direction - int, -1 - is LONG position, 1 - is SHORT\n
        \c commission - float, summarized commission of position, used when \c open_commission and \c close_commission keys is absent\n
        \c open_commission - float, if \c commission key is absent then it will be used as commission for opening deal\n
        \c close_commission - float, if \c commission key is absent then it will be used as commission for opening deal\n
        \c open_datetime - datetime.datetime instance\n
        \c close_datetime - datetime.datetime instance\n
        \c open_points - float, price in points of opening deal\n
        \c close_points - float, price in points of closing deal\n
        \c manual_made - None or something, if not None then considered position and deals assigned made manually\n
        \c do_not_delete - None or something, if not None then considered position will not deleted by some operations
        \exception od_exception.od_exception when first argument is not int or str or has there is no such account
        \return int - id of created position
        \note \ref tacreate_position_from_data must be used instead
        """
        if isinstance(account_id_or_name, (int, long)):
            aid = account_id_or_name
        elif isinstance(account_id_or_name, basestring):
            acc = self.get_account(account_id_or_name)
            if acc <> None:
                aid = acc['id']
            else:
                raise od_exception('There is no such account {0}'.format(account_id_or_name))
        else:
            raise od_exception('account_id_or_name must be int or str')
        if data.has_key('commission'):
            if data.has_key('open_commission') or data.has_key('close_commission'):
                raise od_exception('"open_commission" or "close_commission" key must not appear with "commission" key in "data" parameter')
        else:
            if data.has_key('open_commission') <> data.has_key('close_commission'):
                raise od_exception('"open_commission" must appear within "close_commission" and vise versa in "data" parameter')
        dd = copy(data)
        dd['account_id'] = aid
        remhash(dd, 'commission')
        remhash(dd, 'close_commission')
        remhash(dd, 'open_commission')
        if data.has_key('commission'):
            dd['commission'] = data['commission']
        elif data.has_key('open_commission'):
            dd['commission']= data['open_commission'] + data['close_commission']

        pid = self._sqlite_connection.insert('positions', dd)
        deal_data  = {'manual_made' : gethash(data, 'manual_made'),
                      'account_id' : aid,
                      'position_id' : pid,
                      'paper_id' : data['paper_id'],
                      'count' : data['count']}
        dd1 = copy(deal_data)
        dd1['datetime'] = data['open_datetime']
        dd1['points'] = data['open_points']
        dd1['direction'] = data['direction']
        dd2 = copy(deal_data)
        dd2['datetime'] = data['close_datetime']
        dd2['points'] = data['close_points']
        dd2['direction'] = (- data['direction'])
        if data.has_key('commission'):
            dd1['commission'] = data['commission'] / 2.
            dd2['commission'] = data['commission'] / 2.
        elif data.has_key('open_commission'):
            dd1['commission'] = data['open_commission']
            dd2['commission'] = data['close_commission']
        self._sqlite_connection.insert('deals', dd1)
        self._sqlite_connection.insert('deals', dd2)
        self.recalculate_all_temporary()
                     
    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account_id_or_name, args, **kargs: u'add new position and proper deals in account {0}'.format(account_id_or_name))
    @pass_to_method(create_position_from_data)
    def tacreate_position_from_data(self, *args, **kargs):
        """\brief wrapper for \ref create_position_from_data
        \param account_id_or_name - int or string
        \param data - hash table with keys:\n
        \c paper_id - int, id of paper object\n
        \c count - int, count of contracts\n
        \c direction - int, -1 - is LONG position, 1 - is SHORT\n
        \c commission - float, summarized commission of position\n
        \c open_datetime - datetime.datetime instance\n
        \c close_datetime - datetime.datetime instance\n
        \c open_points - float, price in points of opening deal\n
        \c close_points - float, price in points of closing deal\n
        \c manual_made - None or something, if not None then considered position and deals assigned made manually\n
        \c do_not_delete - None or something, if not None then considered position will not deleted by some operations
        \exception od_exception.od_exception when first argument is not int or str or has there is no such account
        \return int - id of created position
        """
        pass

    @raise_db_closed
    def list_points_view(self, order_by = []):
        """\brief return iterating object for points_view
        \param order_by
        """
        return self._sqlite_connection.execute_select('select * from points_view{0}'.format(order_by_print(order_by)))

    def list_positions(self, account_id = None, paper_id = None, order_by = []):
        """return cursor for getting position descriptions
        \param account_id 
        \param paper_id 
        \param order_by 
        """
        conds = []
        if account_id <> None:
            conds.append(("=", ["account_id"], account_id))
        if paper_id <> None:
            conds.append(("=", ["paper_id"], paper_id))
        return self._sqlite_connection.execute_select_cond("positions", wheres = conds, order_by = order_by)
                          
    
    def get_position_user_attributes(self, position_id, order_by = []):
        """return cursor for user position attributes
        \param position_id 
        """
        return self._sqlite_connection.execute_select_cond("user_position_attributes", wheres = [("=", ["position_id"], position_id)], order_by = order_by)
                                                                                                 
    def get_stored_position_attributes(self, position_id, order_by = []):
        """return cursor for stcored position attributes
        \param position_id 
        \param order_by 
        """
        return self._sqlite_connection.execute_select_cond("stored_position_attributes", wheres = [("=", ["position_id"], position_id)], order_by = order_by)

    def create_group(self, deal_id):
        """return id the group maked from deals
        \param deal_id  int or list of ints
        """
        paper_id = None
        account_id = None
        direction = None
        gid = None
        for did in (isinstance(deal_id, int) and [deal_id] or deal_id):
            deal = self._sqlite_connection.execute_select("select * from deals where id = ?", [did]).fetchall()[0]
            if paper_id == direction == gid == account_id == None:
                paper_id = deal["paper_id"]
                direction = deal["direction"]
                account_id = deal["account_id"]
                gid = self._sqlite_connection.insert("deal_groups", {"paper_id" : paper_id,
                                                                     "account_id" : account_id,
                                                                     "direction" : direction})
            else:
                assert(paper_id == deal["paper_id"])
                assert(direction == deal["direction"])
                assert(account_id == deal["account_id"])
            self._sqlite_connection.insert("deal_group_assign", {"deal_id" : did, "group_id" : gid})
        return gid

    def add_to_group(self, group_id, deal_id):
        """add deals to group
        \param group_id 
        \param deal_id 
        """
        g = self._sqlite_connection.execute_select("select * from deal_groups where id = ?", [group_id]).fetchall()[0]
        for di in (isinstance(deal_id, int) and [deal_id] or deal_id):
            (c,) = self._sqlite_connection.execute("select count(*) from deals where id = ? and paper_id = ? and direction = ? and account_id = ?", [di, g["paper_id"], g["direction"], g["account_id"]]).fetchone()
            assert(c == 1)
            self._sqlite_connection.insert("deal_group_assign", {"group_id" : group_id,
                                                                 "deal_id" : di})
            

            
    def calculate_deals(self, account_id, deal_id = None):
        """Recalculate temporary table deals_view starting from deal_id 
        \param account_id 
        \param paper_id 
        \param deal_id 
        """
        # if deal_id == None:
        cur = self._sqlite_connection.execute_select("select d.* from deals d where d.account_id = ? and not exists(select dd.* from deals dd where dd.parent_deal_id = d.id) order by d.datetime", [account_id])
        (mc, ) = self._sqlite_connection.execute("select a.money_count from accounts a where a.id = ?", [account_id]).fetchone()
        self._calculate_deals_with_initial(cur, mc, {})
        # else:
        #     cur = self._sqlite_connection.execute_select("select d.* from deals d, deals dd where dd.id = ? and d.datetime >= dd.datetime and d.id >= dd.id and d.account_id = ? and not exists(select ddd.* from deals ddd where ddd.parent_deal_id = d.id) order by d.datetime, d.id", [deal_id, account_id])
        #     (mc, pbl) = self._sqlite_connection.execute("select dw.net_after, dw.paper_ballance_after from deals_view dw inner join deals d on dw.deal_id = d.id where d.id = ?", [deal_id]).fetchone() or (None, None)
        #     if mc == None:
        #         return self.calculate_deals(account_id, paper_id)
        #     self._calculate_deals_with_initial(cur, mc, pbl)
                                     
    def _calculate_deals_with_initial(self, cursor, money, paper_ballance):
        """calculates deals given in cursor
        \param cursor 
        \param money  net before the deals returned by cursor
        \param paper_ballance hash table {paper id : ballance for paper}
        """
        def addition(h, m, p):
            h["datetime_formated"] = h["datetime"].isoformat()
            h["date"] = h["datetime"].date()
            h["date_formated"] = h["date"].isoformat()
            h["time"] = h["datetime"].time()
            h["time_formated"] = h["time"].isoformat()
            h["day_of_week"] = h["datetime"].weekday()
            h["day_of_week_formated"] = h["datetime"].strftime("%a")
            h["month"] = h["datetime"].month
            h["month_formated"] = h["datetime"].strftime("%b")
            h["year"] = h["datetime"].year
            h["price"] = h["point"] * h["points"]
            h["price_formated"] = "{0}{1}".format(h["price"], h["money_name"])
            h["volume"] = h["price"] * h["count"]
            h["volume_formated"] = "{0}{1}".format(h["volume"], h["money_name"])
            h["direction_formated"] = (h["direction"] >= 0 and "S" or "L")
            h["net_before"] = m
            h["net_after"] = m + (h["volume"] * h["direction"] / abs(h["direction"])) - h["commission"]
            h["paper_ballance_before"] = p
            h["paper_ballance_after"] = p - (h["count"] * h["direction"] / abs(h["direction"]))
            (h["user_attributes_formated"], ) = self._sqlite_connection.execute("select string_reduce(argument_value(a.name, a.value)) from user_deal_attributes a where a.deal_id = ? group by a.deal_id", [h["deal_id"]]).fetchone() or (None,)
            return (h["net_after"], h["paper_ballance_after"])
            
        inserts = []
        net = money
        bal = copy(paper_ballance)
        for dd in cursor:
            newdw = copy(dd)
            del newdw["id"]
            del newdw["sha1"]
            del newdw["parent_deal_id"]
            newdw["deal_id"] = dd["id"]
            (newdw["paper_type"], newdw["paper_class"], newdw["paper_name"]) = self._sqlite_connection.execute("select p.type, p.class, p.name from papers p inner join deals d on d.paper_id = p.id where d.id = ?", [dd["id"]]).fetchone()
            (newdw["money_name"], newdw["money_id"]) = self._sqlite_connection.execute("select m.name, m.id from moneys m inner join accounts a on a.money_id = m.id inner join deals d on d.account_id = a.id where d.id = ?", [dd["id"]]).fetchone()
            (newdw["point"], newdw["step"]) = self._sqlite_connection.execute("select pn.point, pn.step from points pn inner join accounts a on a.money_id = pn.money_id inner join deals d on d.account_id = a.id and d.paper_id = pn.paper_id where d.id = ?", [dd["id"]]).fetchone() or (1, 1)
            (net, bal[dd["paper_id"]]) = addition(newdw, net, (gethash(bal, dd["paper_id"]) <> None and gethash(bal, dd["paper_id"]) or 0))
            inserts.append(newdw)
        if len(inserts) > 0:
            self._sqlite_connection.insert("deals_view", inserts)

    def recalculate_deals(self, account_id, deal_id = None):
        """removes and recalculate additional table for deals
        \param account_id 
        \param paper_id 
        """
        # if deal_id == None:
        self._sqlite_connection.execute("delete from deals_view where account_id = ?", [account_id])
        self._sqlite_connection.execute("delete from deals_view where id in (select dw.id from deals_view dw inner join deals d on dw.deal_id = d.id where d.account_id = ?)", [account_id])
        self.calculate_deals(account_id)
        # else:
        #     self._sqlite_connection.execute("delete from deals_view where id in (select dv.id from deals_view dv inner join deals d on dv.deal_id = d.id, deals dd where dd.id = ? and d.account_id = ? and d.paper_id = ? and d.datetime >= dd.datetime)", [deal_id, account_id, paper_id])
        #     self.calculate_deals(account_id, paper_id, deal_id)

    # def __recalculate_deals__(self, account_id, paper_id, *args, **kargs):
    #     """
    #     - `account_id`:
    #     - `paper_id`:
    #     - `*args`:
    #     - `**kargs`:
    #     """
    #     self.recalculate_deals(account_id, paper_id)


    def make_groups(self, account_id, paper_id, time_distance = 5):
        """
        \param account_id 
        \param paper_id 
        \param time_distance max time difference between deals in one group
        """
        gid = None
        for dd in self._sqlite_connection.execute_select("select d.* from deals d inner join deals_view dd on dd.deal_id = d.id where d.position_id is null and d.account_id = ? and d.paper_id = ? order by d.datetime", [account_id, paper_id]):
            if gid == None:
                gid = self.create_group(dd["id"])
            else:
                gg = self._sqlite_connection.execute_select("select max(d.datetime) as d, g.account_id as account_id, g.paper_id as pid, g.direction as dir from deals d inner join deal_group_assign gd on gd.deal_id = d.id inner join deal_groups g on gd.group_id = g.id where g.id = ? group by g.id", [gid]).fetchall()[0]
                if gg["pid"] == dd["paper_id"] and gg["dir"] == dd["direction"] and dd["account_id"] == gg["account_id"] and dd["datetime"] - any_to_datetime(gg["d"]) <= timedelta(0, time_distance):
                    self.add_to_group(gid, dd["id"])
                else:
                    gid = self.create_group(dd["id"])

    def remake_groups(self, account_id, paper_id, time_distance = 5):
        """delete all groups and remake it again
        \param account_id 
        \param paper_id 
        \param time_distance 
        """
        self._sqlite_connection.execute("delete from deal_groups where id in (select distinct g.id from deal_groups g inner join deal_group_assign dg on dg.group_id = g.id inner join deals d on dg.deal_id = d.id where d.account_id = ? and d.paper_id = ?)", [account_id, paper_id])
        self._sqlite_connection.execute("delete from deal_groups where account_id = ? and paper_id = ?", [account_id, paper_id])
        self.make_groups(account_id, paper_id, time_distance)
                
    def list_groups(self, account_id, paper_id):
        """
        \param account_id 
        \param paper_id 
        """
        return self._sqlite_connection.execute_select("select g.* from deal_groups g inner join deal_group_assign dg on dg.group_id = g.id inner join deals d on dg.deal_id = d.id  where d.account_id = ? and d.paper_id = ? group by g.id", [account_id, paper_id])

    
    def __remake_groups(self, account_id, paper_id, time_distance = 5, *args, **kargs):
        """
        \param account_id 
        \param paper_id 
        \param time_distance 
        \param *args 
        \param **kargs 
        """
        self.remake_groups(account_id, paper_id, time_distance)

    def make_positions_for_whole_account(self, account_id_or_name, time_distance = 5):
        """\brief makes posision objects for all papers for which deals exists in this account
        \param account_id_or_name - int or str
        \param time_distance - number, pass to \ref make_positions
        \exception od_exception.od_exception when first argument is not a number or str
        \note \ref tamake_positions_for_whole_account must be used instead by model
        """
        aid = None
        if isinstance(account_id_or_name, (int, long)):
            aid = account_id_or_name
        elif isinstance(account_id_or_name, basestring):
            acc = self.get_account(account_id_or_name)
            if acc <> None:
                aid = acc["id"]
            else:
                return
        else:
            raise od_exception("account_id_or_name must be int or str")
        
        for (paper, ) in self._sqlite_connection.execute('select distinct paper_id from deals where account_id = ?', [aid]):
            self.make_positions(aid, paper, time_distance)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account_id_or_name, *args, **kargs: u'auto make positions for account {0}'.format(account_id_or_name))
    @pass_to_method(make_positions_for_whole_account)
    def tamake_positions_for_whole_account(self, *args, **kargs):
        """\brief wrapper around \ref make_positions_for_whole_account
        \param account_id_or_name - int or str
        \param time_distance - number, pass to \ref make_positions
        """
        pass

    def make_positions(self, account_id, paper_id, time_distance = 5):
        """automatically makes positions
        \param account_id 
        \param paper_id 
        \param time_distance  time distance for make_groups
        """
        self.remake_groups(account_id, paper_id, time_distance)
        hashes = []
        def go_on():
            g1 = self._sqlite_connection.execute_select("select * from (select g.id as id, g.direction as direction, min(d.datetime) as mindatetime, max(d.datetime) as maxdatetime from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on g.id = dg.group_id where g.account_id = ? and g.paper_id = ? group by g.id) order by maxdatetime, mindatetime limit 1", [account_id, paper_id]).fetchall()
            if len(g1) == 0:
                return False
            g1 = g1[0]
            g2 = self._sqlite_connection.execute_select("select * from (select g.id as id, g.direction as direction, min(d.datetime) as mindatetime, max(d.datetime) as maxdatetime from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on g.id = dg.group_id where g.account_id = ? and g.paper_id = ? and g.direction = ? group by g.id) where mindatetime >= ? order by maxdatetime, mindatetime limit 1", [account_id, paper_id, -(g1["direction"]), g1["maxdatetime"]]).fetchall()
            if len(g2) == 0:
                return False
            g2 = g2[0]
            (g1, g2) = self.try_make_ballanced_groups(g1["id"], g2["id"])
            hashes.append(self.create_position_hash(g1, g2))
            self._sqlite_connection.executemany("delete from deal_groups where id = ?", [(g1,), (g2,)])
            return True
        while go_on():
            pass
        self._create_position_raw(hashes)

        
    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account_id, paper_id, *args, **kargs: "automake positions for acc {0} and paper {1}".format(account_id, paper_id))
    @pass_to_method(make_positions)
    def tamake_positions(self, *args, **kargs):
        """transacted wrapper oround make_positions
        \param account_id 
        \param paper_id 
        \param time_distance  time distance for make_groups
        """
        pass

    def remove_position(self, pid):
        """\brief remove one or more positions
        \param pid - int or list of ints, position id one or more
        \note \ref taremove_position must be used instead
        """
        pids = (isinstance(pid, (int, long)) and [pid] or pid)
        self._sqlite_connection.executemany('delete from positions where id = ?', map(lambda a: (a,), pids))
        for (acc, ) in self._sqlite_connection.execute('select id from accounts'):
            self.recalculate_positions(acc)

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, pid: (isinstance(pid, (int, long)) and u'remove position with id {0}'.format(pid) or u'remove {0} positions'.format(len(pid))))
    @pass_to_method(remove_position)
    def taremove_position(self, *args, **kargs):
        """\brief wrapper for \ref remove_position 
        """
        pass

    


    def try_make_ballanced_groups(self, gid1, gid2):
        """if count of papers for gid1 and gid2 is the same then just return gid1 and gid2,
        else just split gid1 or gid2 to the minimal count papers and return splited gids
        \param gid1  group_id
        \param gid2 
        """
        (c1, c2) = map(lambda a: self._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [a]).fetchone()[0], [gid1, gid2])
        assert(c1 > 0 and c2 > 0)
        if c1 == c2:
            return (gid1, gid2)
        elif c1 > c2:
            (g, gg) = self.split_group(gid1, c2)
            return (g, gid2)
        else:
            (g, gg) = self.split_group(gid2, c1)
            return (gid1, g)

    # def __recalculate_deals_by_group_id__(self, gid, *args, **kargs):
    #     """
    #     - `gid`:
    #     - `*args`:
    #     - `**kargs`:
    #     """
    #     (account_id, paper_id) = self._sqlite_connection.execute("select account_id, paper_id from deal_groups where id = ?", [gid]).fetchone()
    #     self.recalculate_deals(account_id, paper_id)


    def split_group(self, gid, count):
        """return tuple (gid1, gid2)
        if count >= sum of counts all deals assigned to group `gid` then gid2 = None
        \param gid  Group id split to
        \param count  count of papers of papers assigned to gid1
        """
        (c, ) = self._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [gid]).fetchone()
        if c <= count:
            return (gid, None)
        else:
            deals = []
            summ = 0
            for deal in self._sqlite_connection.execute_select("select d.* from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? order by d.datetime", [gid]):
                deals.append(deal["id"])
                summ += deal["count"]
                if summ == count:
                    return (self.create_group(deals), gid)
                elif summ > count:
                    self.remove_from_group(deals[-1])
                    (d, dd) = self.split_deal(deals[-1], deal["count"] - (summ - count))
                    self.add_to_group(gid, dd)
                    return (self.create_group(deals[:-1] + [d]), gid)

    def remove_from_group(self, deal_id):
        """remove deal(s) from group
        \param gid 
        \param deal_id 
        """
        deals = map(lambda a: (a,), (isinstance(deal_id, int) and [deal_id] or deal_id))
        self._sqlite_connection.executemany("delete from deal_group_assign where deal_id = ?", deals)


    def split_deal(self, deal_id, count):
        """return tuple with 2 deal_id. One is the deal with `count` papers, second with remainder
        if count of deal is less or equal to `count` then return tuple (deal_id, None)
        \param deal_id 
        \param count  needed count of papers for deal
        """
        deal = self._sqlite_connection.execute_select("select * from deals where id = ?",[deal_id]).fetchall()[0]
        if count >= deal["count"]:
            return (deal["id"], None)
        else:
            nd1 = copy(deal)
            del nd1["id"]
            remhash(nd1, 'sha1')
            remhash(nd1, 'commission')
            nd1["parent_deal_id"] = deal["id"]
            nd2 = copy(nd1)
            nd1["count"] = count
            nd2["count"] = deal["count"] - count
            nd1['commission'] = deal['commission'] / deal['count'] * nd1['count']
            nd2['commission'] = deal['commission'] / deal['count'] * nd2['count']
            (pap, mon) = self._sqlite_connection.execute("select paper_ballance_before, net_before from deals_view where deal_id = ?", [deal_id]).fetchone()
            self.create_deal(deal['account_id'], [nd1, nd2], do_recalc = False)
            self._sqlite_connection.execute("delete from deals_view where deal_id = ?", [deal_id])
            (d1, d2) = map(lambda a: a[0], self._sqlite_connection.execute("select id from deals where parent_deal_id = ?", [deal_id]))
            self._calculate_deals_with_initial(self._sqlite_connection.execute_select("select * from deals where id = ? or id = ?", [d1, d2]), mon, {deal["paper_id"] : pap})
            
            return (d1, d2)
            

    def start_action(self, action_name):
        """starts new action with an action name
        Arguments:
        \param action_name 
        """
        ab = self._sqlite_connection.execute("select count(h1.id) from history_steps h1, current_history_position ch where h1.id > ch.step_id").fetchone()[0]
        if ab > 0:
            raise od_exception_action_cannot_create(ab)
        aid = self._sqlite_connection.insert("history_steps", {"autoname" : action_name,
                                                               "datetime" : datetime.now()})
        self._sqlite_connection.insert("current_history_position", {"step_id" : aid})
        
    def end_action(self, ):
        """ends an action recording
        """
        self._sqlite_connection.execute("delete from current_history_position")

    def list_actions(self, order_by = ["id"]):
        """list all actions executed
        """
        return self._sqlite_connection.execute_select_cond("history_steps", order_by = order_by)

    def get_current_action(self, ):
        """return current action or None if no one set
        """
        a = self._sqlite_connection.execute_select("select h.* from history_steps h inner join current_history_position c on c.step_id = h.id").fetchall()
        if len(a) > 0:
            return a[0]
        else:
            return None

    def set_current_action(self, action_id = None):
        """set current action to action_id
        \param action_id id of action to set or None to delete current action
        """
        if action_id == None:
            self._sqlite_connection.execute("delete from current_history_position")
        else:
            (g, ) = self._sqlite_connection.execute("select id from history_steps where id = ?", [action_id]).fetchone() or (None, )
            if g == None:
                raise od_exception_action_does_not_exists()
            self._sqlite_connection.insert("current_history_position", {"step_id" : action_id})
        

        
    def calculate_positions(self, aid, pid = None):
        """
        Arguments:
        \param aid 
        \param paid 
        \param pid 
        """
        # if pid == None:
        cur = self._sqlite_connection.execute_select("select * from positions order by close_datetime, open_datetime")
        net = self.get_account(aid)["money_count"]
        self._calculate_positions_with_initial(cur, net, net)
        # else:
        #     cur = self._sqlite_connection.execute_select("select p.* from positions p, positions pp where pp.id = ? and p.close_datetime >= pp.close_datetime order by close_datetime, open_datetime",[pid])
        #     (net, gross) = self._sqlite_connection.execute("select net_after, gross_after from positions_view where position_id = ?", [pid]).fetchone() or (None, None)
        #     if net == gross == None:
        #         return self.recalculate_positions(aid, paid)
        #     self._calculate_positions_with_initial(cur, net, gross)

    def _calculate_positions_with_initial(self, cursor, net, gross):
        """
        \param cursor 
        \param net  net start from
        \param gross  gross start from
        """
        def do_the_work(post, netx, grossx):
            post["direction_formated"] = (post["direction"] > 0 and "S" or "L")
            for c in ["open_", "close_"]:
                post["{0}price".format(c)] = post["{0}points".format(c)] * post["point"]
                post["{0}price_formated".format(c)] = u"{0}{1}".format(post["{0}price".format(c)], post["money_name"])
                post["{0}volume".format(c)] = post["{0}price".format(c)] * post["count"]
                post["{0}volume_formated".format(c)] = u'{0}{1}'.format(post["{0}volume".format(c)], post["money_name"])
                post["{0}datetime_formated".format(c)] = post["{0}datetime".format(c)].strftime("%Y-%m-%d %H:%M:%S")
                post["{0}date".format(c)] = post["{0}datetime".format(c)].date()
                post['{0}time'.format(c)] = post["{0}datetime".format(c)].time()
                post['{0}date_formated'.format(c)] = post['{0}datetime'.format(c)].strftime("%d-%m-%Y")
                post['{0}time_formated'.format(c)] = post['{0}time'.format(c)].isoformat()
                post['{0}day_of_week'.format(c)] = post['{0}datetime'.format(c)].weekday()
                post['{0}day_of_week_formated'.format(c)] = post['{0}datetime'.format(c)].strftime("%a")
                post['{0}month'.format(c)] = post['{0}datetime'.format(c)].month
                post['{0}month_formated'.format(c)] = post['{0}datetime'.format(c)].strftime("%b")
                post['{0}year'.format(c)] = post['{0}datetime'.format(c)].year

            post["duration"] = post["close_datetime"] - post["open_datetime"]
            post["duration_formated"] = post["duration"].__str__()
            post["points_range"] =  (post["open_points"] - post["close_points"]) * post["direction"]
            post["points_range_abs"] = abs(post["points_range"])
            post["points_range_abs_formated"] = (post["points_range"] < 0 and "({0})" or "{0}").format(post["points_range_abs"])
            post["price_range"] = post["points_range"] * post["point"]
            post["price_range_abs"] = post["points_range_abs"] * post["point"]
            post["price_range_abs_formated"] = (post["price_range"] < 0 and "({0})" or "{0}").format(post["price_range_abs"])
            post["pl_gross"] = post["price_range"] * post["count"]
            post["pl_gross_abs"] = abs(post["pl_gross"])
            post["pl_gross_abs_formated"] = (post["pl_gross"] < 0 and "({0})" or "{0}").format(post["pl_gross_abs"])
            post["pl_net"] = post["pl_gross"] - post["commission"]
            post["pl_net_abs"] = abs(post["pl_net"])
            post["pl_net_abs_formated"] = (post["pl_net"] < 0 and "({0})" or "{0}").format(post["pl_net_abs"])
            try:
                post["steps_range"] = post["points_range"] / post["step"]
            except ZeroDivisionError:
                post["steps_range"] = 0
            post["steps_range_abs"] = abs(post["steps_range"])
            post["steps_range_abs_formated"] = format_abs_value(post["steps_range"])
            try:
                post["percent_range"] = post["pl_net"] / netx * 100
            except ZeroDivisionError:
                post["percent_range"] = 0
            post["percent_range_abs"] = abs(post["percent_range"])
            post["percent_range_abs_formated"] = format_abs_value(post["percent_range"])
            try:
                post['percent_volume_range'] = post['pl_net'] / post['open_volume'] * 100
            except ZeroDivisionError:
                post['percent_volume_range'] = 0
            post['percent_volume_range_abs'] = abs(post['percent_volume_range'])
            post['percent_volume_range_abs_formated'] = format_abs_value(post['percent_volume_range'])
            try:
                post['percent_comm_plgross'] = post['commission'] / post['pl_gross']
            except ZeroDivisionError:
                post['percent_comm_plgross'] = 0
            post['percent_comm_plgross_abs'] = abs(post['percent_comm_plgross'])
            post['percent_comm_plgross_abs_formated'] = format_abs_value(post['percent_comm_plgross'])
            post['price_avg'] = (post['open_price'] + post['close_price']) / 2.
            post['volume_avg'] = (post['open_volume'] + post['close_volume']) / 2.
            post["net_before"] = netx
            post["net_after"] = netx + post["pl_net"]
            post["gross_before"] = grossx
            post["gross_after"] = grossx + post["pl_gross"]
            return (post["net_after"], post["gross_after"])
          
        n = net
        g = gross
        ins = []
        for pos in cursor:
            posx = copy(pos)
            del posx["id"]
            posx["position_id"] = pos["id"]
            (posx["money_id"], posx["money_name"]) = self._sqlite_connection.execute("select m.id, m.name from moneys m inner join accounts a on a.money_id = m.id inner join positions p on p.account_id = a.id where p.id = ?", [pos["id"]]).fetchone()
            (posx["point"], posx["step"]) = self._sqlite_connection.execute("select point, step from points where money_id = ? and paper_id = ?", [posx["money_id"], posx["paper_id"]]).fetchone() or (1, 1)
            (posx["paper_type"], posx["paper_stock"], posx["paper_class"], posx["paper_name"]) = self._sqlite_connection.execute("select type, stock, class, name from papers where id = ?", [posx["paper_id"]]).fetchone()
            # if first:
            #     common = {}
            #     (paper_id, ) = self._sqlite_connection.execute("select paper_id from positions where id = ? limit 1", [pos["id"]]).fetchone()
            #     (common["money_id"], common["money_name"]) = self._sqlite_connection.execute("select m.id, m.name from moneys m inner join accounts a on a.money_id = m.id where a.id = ? limit 1", [pos["account_id"]]).fetchone()
            #     (common["point"], common["step"]) = self._sqlite_connection.execute("select point, step from points where money_id = ? and paper_id = ?", [common["money_id"], paper_id]).fetchone() or (1, 1)
            #     (common["paper_type"], common["paper_stock"], common["paper_class"], common["paper_name"]) = self._sqlite_connection.execute("select type, stock, class, name from papers where id = ?", [paper_id]).fetchone()
            # add_hash(posx, common)
            (n, g) = do_the_work(posx, n, g)
            ins.append(posx)
        if len(ins) > 0:
            self._sqlite_connection.insert("positions_view", ins)
            

    def recalculate_positions(self, aid, position_id = None):
        """
        Arguments:
        \param aid  account id
        \param position_id  id of position recalculate from
        \todo make position_id be realy usable argument
        """
        # if position_id == None:
        self._sqlite_connection.execute("delete from positions_view where account_id = ?", [aid])
        self._sqlite_connection.execute("delete from positions_view where id in (select pw.id from positions_view pw inner join positions p on p.id = pw.position_id where p.account_id = ?)",[aid])
        self.calculate_positions(aid)
        # else:
        #     self._sqlite_connection.execute("delete from positions_view where id in (select pv.id from positions_view pv inner join positions p on pv.position_id = p.id, positions pp where pp.id = ? and ((p.account_id = ? and p.paper_id = ?) or (pv.account_id = ? and pv.paper_id = ?)) and p.close_datetime >= pp.close_datetime)", [position_id, aid, paid, aid, paid])
        #     self.calculate_positions(aid, paid, position_id)

    def go_to_action(self, action_id):
        """roll back or forward to the action
        Arguments:
        \param action_id 
        """
        a = self.get_current_action()
        if a <> None and action_id == a["id"]:
            return
        l = self._sqlite_connection.execute_select("select * from history_steps order by id desc limit 1").fetchall() # последнее действие
        if len(l) > 0:
            l = l[0]
        else:
            return                      # нет действий в базе - ничего не делаем
        gac = self._sqlite_connection.execute_select("select * from history_steps where id = ?", [action_id]).fetchall()
        if len(gac) == 0:
            raise od_exception_action_does_not_exists() # отсутствует такое действие в базе - выбрасываем исключение
        else:
            gac = gac[0]
        if a == None or a["id"] == l["id"]:
            a = l
        if a["id"] < action_id <= l["id"]: # нужно сделать redo
            self._redo_to_action(a["id"], gac["id"])
        elif action_id < a["id"] <= l["id"]: # делаем undo
            self._undo_to_action(a["id"], gac["id"])
        self.recalculate_all_temporary()

    def clear_temporary_tables(self, ):
        """execute `delete` operator for all temporary tables
        """
        for table in ["account_statistics", "deals_view", "positions_view", "deal_groups", "deal_group_assign", "deal_paper_selected", "deal_account_selected", "position_account_selected", "position_paper_selected"]:
            self._sqlite_connection.execute("delete from {0}".format(table))

            
    def _redo_to_action(self, start_id, end_id):
        """redo all actions from the first action after the `start_id` to the `end_id` including
        Arguments:
        \param start_id 
        \param end_id 
        """
        self.set_current_action()
        maked = None
        for (action_id, ) in self._sqlite_connection.execute("select id from history_steps where id > ? and id <= ? order by id", [start_id, end_id]):
            self._redo_action(action_id)
            maked = action_id
        if maked <> None:
            self.set_current_action(maked)
        self._clear_unassigned_undo_redo()

    def _redo_action(self, action_id):
        """executes all queries for this action in direct order
        Arguments:
        \param action_id id of action execute queries from
        """
        # print("========== REDOING action {0} ===========".format(action_id))
        for (q, ) in self._sqlite_connection.execute("select query from redo_queries where step_id = ? order by id", [action_id]):
            self._sqlite_connection.execute(q)
          #  print("REDO:: {0}".format(q))

    def _undo_to_action(self, start_id, end_id):
        """undo all actions from `start_id` to the first action after `end_id` including in reverse order
        Arguments:
        \param start_id 
        \param end_id 
        """
        self.set_current_action()
        maked = None
        for (action_id, ) in self._sqlite_connection.execute("select id from history_steps where id > ? and id <= ? order by id desc", [end_id, start_id]):
            self._undo_action(action_id)
            maked = action_id
        if maked <> None:
            self.set_current_action(end_id)
        self._clear_unassigned_undo_redo()

    def _undo_action(self, action_id):
        """execute queries assigned to action in reverse order
        Arguments:
        \param action_id 
        """
    #    print("============= UNDOING action {0} ==============".format(action_id))
        for (q, ) in self._sqlite_connection.execute("select query from undo_queries where step_id = ? order by id desc", [action_id]):
            self._sqlite_connection.execute(q)
     #       print("UNDO: {0}".format(q))

    def _clear_unassigned_undo_redo(self, ):
        """clear all undo / redo queries not assigned to any action
        """
        self._sqlite_connection.execute("delete from undo_queries where id in (select id from undo_queries q where not exists(select h.* from history_steps h where h.id = q.step_id))")
        self._sqlite_connection.execute("delete from redo_queries where id in (select id from redo_queries q where not exists(select h.* from history_steps h where h.id = q.step_id))")

    def recalculate_all_temporary(self, ):
        """recalculate all temporary tables in the database
        """
        for (aid, ) in self._sqlite_connection.execute("select distinct account_id from deals"):
            self.recalculate_deals(aid)
            self.recalculate_positions(aid)

    
    def set_current_account(self, id_or_name):
        """\brief set given account as current
        \param id_or_name id or name or None to remove current account property
        \exception exceptions.od_exception there is not account with that name or id
        \note this method must not be used by view, view must use \ref taset_current_account
        """
        if id_or_name == None:
            self.remove_global_data("current_account")
            return
        acc = self.get_account(id_or_name)
        if acc == None:
            raise od_exception("There is not account {0}".format(id_or_name))
        self.add_global_data({"current_account" : acc["id"]})

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, ion: "set {0} as current account".format(ion))
    @pass_to_method(set_current_account)
    def taset_current_account(self, id_or_name):
        """\brief wrapper around \ref set_current_account
        \param id_or_name id or name or None to remove current account property
        """
        pass


    def get_current_account(self, ):
        """\brief get current account
        \retval hash table with account (like get_account does)
        \retval None if no one account selected as current
        """
        aid = self.get_global_data("current_account")
        if aid == None:
            return None
        return self.get_account(aid)

    def shrink_money_by_id(self, id_list):
        """\brief delete all money objects which id is not in list
        \param id_list list of id's
        \note \ref tashrink_money_by_id must be used by view instead
        """
        self._sqlite_connection.execute("delete from moneys where id not in ({0})".format(reduce_by_string(", ", id_list)))


    @raise_db_closed
    @in_transaction
    @in_action(lambda self, id_list: "delete {0} money objects".format(len(id_list)))
    @pass_to_method(shrink_money_by_id)
    def tashrink_money_by_id(self, *args, **kargs):
        """\brief wrapper around \ref shrink_money_by_id
        \param id_list list of id's
        """
        pass

        


    def list_view_accounts(self, order_by = []):
        """\brief list the output of accounts_view
        \param order_by order by list
        \return iterator returning list list of hashes with keys account_id, name, money_name, first_money, current_money, deals, positions
        """
        return self._sqlite_connection.execute_select("select * from accounts_view {0}".format(order_by_print(order_by)))

    def change_money(self, id_or_name, name = None, full_name = None):
        """\brief change existing money 
        \param id_or_name
        \param name new name to set or None
        \param full_name new full name to set or None
        \note view must use \ref tachange_money insted
        """
        sets = {}
        if not is_null_or_empty(name):
            sets["name"] = name
        if not is_null_or_empty(full_name):
            sets["full_name"] = full_name

        money = self.get_money(id_or_name)
        self._sqlite_connection.update("moneys", sets, "id = ?", (money["id"], ))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, id_or_name, *args, **kargs: "change money with {0}".format(id_or_name))
    @pass_to_method(change_money)
    def tachange_money(self, *args, **kargs):
        """\brief transacted wrapper to \ref change_money
        \param id_or_name
        \param name new name to set or None
        \param full_name new full name to set or None
        """
        pass

    def assigned_account_deals(self, id_or_name):
        """\brief return count of assigned deals to account
        \param id_or_name name or id of account
        \return int - count of deals
        \exception od_exception_db_error if there is no such account
        """
        acc = self.get_account(id_or_name)
        if acc == None:
            raise od_exception_db_error("There is no such account \"{0}\"".format(id_or_name))
        (c, ) = self._sqlite_connection.execute("select count(d.id) from deals d inner join accounts a on d.account_id = a.id where a.id = ?", [acc["id"]]).fetchone()
        return c


    def assigned_account_positions(self, id_or_name):
        """\brief return count of assigned positions to account
        \param id_or_name
        \return int - count of positions
        \exception od_exception_db_error if there is no such account
        """
        acc = self.get_account(id_or_name)
        if acc == None:
            raise od_exception_db_error("There is no such account \"{0}\"".format(id_or_name))
        (c, ) = self._sqlite_connection.execute("select count(p.id) from positions p inner join accounts a on p.account_id = a.id where a.id = ?", [acc["id"]]).fetchone()
        return c

    def change_deals(self, deal_id, fields, do_recalc = True):
        """\brief change one or more deal
        \param deal_id int or list of int with deal id's
        \param fields hash table with one or more keys:\n
        sha1\n
        manual_made - None or not None\n
        parent_deal_id - None or int\n
        account_id - int\n
        position_id - None or int\n
        paper_id - int\n
        count - int\n
        direction - -1 means BUY, 1 means SELL\n
        points - float\n
        commission - float\n
        datetime - datetime.datetime instance
        user_attributes - hash table, if exists then user attributes will be rewriten
        stored_attributes - hash table, if exists then stored attributes will be rewriten
        \param do_recalc - if True (default), after changing deal all temporary tables will be recalculated
        \note view must use \ref tachange_deals instead
        \todo make do_recalc behaviour more smart: if paper changes then reclculate data for previous paper and for current, if does not then recalculate just for this paper (may be it is not need at all)
        """
        if is_null_or_empty(deal_id):
            raise od_exception("deal_id can not be empty")
        
        ids = (isinstance(deal_id, (int, long)) and [deal_id] or deal_id)
        ids = map(lambda a: (a, ), ids)
        if is_null_or_empty(fields):
            return
        newfields = copy(fields)
        remhash(newfields, "user_attributes")
        remhash(newfields, "stored_attributes")
        self._sqlite_connection.update("deals", newfields, "id = ?", ids)

        if fields.has_key("user_attributes"):
            atts = fields["user_attributes"]
            self._sqlite_connection.execute("delete from user_deal_attributes where deal_id = ?", [deal_id])
            ins_data = map(lambda k: {"deal_id" : deal_id, "name" : k, "value" : atts[k]}, atts.keys())
            if not is_null_or_empty(ins_data):
                self._sqlite_connection.insert("user_deal_attributes", ins_data)

        if fields.has_key("stored_attributes"):
            atts = fields["stored_attributes"]
            self._sqlite_connection.execute("delete from stored_deal_attributes where deal_id = ?", [deal_id])
            ins_data = map(lambda k: {"deal_id" : deal_id, "type" : k, "value" : atts[k]}, atts.keys())
            if not is_null_or_empty(ins_data):
                self._sqlite_connection.insert("stored_deal_attributes", ins_data)
                                                                    
        self.fix_groups()
        self.fix_positions()
        self.recalculate_all_temporary()
        if do_recalc:
            self.recalculate_all_temporary()
        
    @raise_db_closed
    @in_transaction
    @in_action(lambda self, did, *args, **kargs: (isinstance(did, (int, long)) and "change deal with id {0}".format(did) or "change {0} deals".format(len(did))))
    @pass_to_method(change_deals)
    def tachange_deals(self, *args, **kargs):
        """\brief wrapper around \ref change_deals
        \param deal_id int or list of int with deal id's
        \param fields hash table with one or more keys:\n
        \c sha1\n
        \c manual_made - None or not None\n
        \c parent_deal_id - None or int\n
        \c account_id - int\n
        \c position_id - None or int\n
        \c paper_id - int\n
        \c count - int\n
        \c direction - -1 means BUY, 1 means SELL\n
        \c points - float\n
        \c commission - float\n
        \c datetime - datetime.datetime instance
        \param do_recalc - if True (default), after changing deal all temporary tables will be recalculated
        """
        pass

    def get_deal(self, deal_id):
        """\brief get deal_id from the database
        \param deal_id id of the deal
        \retval None if there is not deal with such id
        \retval hash table with keys:\n
        \c id - int, id\n
        \c sha1\n
        \c manual_made - None or not None\n
        \c parent_deal_id - None or int\n
        \c account_id - int\n
        \c position_id - None or int\n
        \c paper_id - int\n
        \c count - int\n
        \c direction - -1 means BUY, 1 means SELL\n
        \c points - float\n
        \c commission - float\n
        \c datetime - datetime.datetime instance\n
        \c user_attributes - hash table {key : value} with user attributes assigned to deal or without key if does not exists\n
        \c stored_attributes - hash table with not user attributes or without key if does not exists
        """
        ret = self._sqlite_connection.execute_select("select * from deals where id = ?", [deal_id]).fetchone()
        if ret <> None:
            uat = self._sqlite_connection.execute_select("select name, value from user_deal_attributes where deal_id = ?", [deal_id]).fetchall() # the list of hash tables
            if len(uat) > 0:
                ats = {}
                for k in uat:
                    ats[k["name"]] = k["value"]
                ret["user_attributes"] = ats
            sat = self._sqlite_connection.execute_select("select type, value from stored_deal_attributes where deal_id = ?", [deal_id]).fetchall()
            if len(sat) > 0:
                ats = {}
                for k in sat:
                    ats[k["type"]] = k["value"]
                ret["stored_attributes"] = ats
        return ret
                    
    def list_deals_view_with_condition(self, condition, condargs,  order_by = []):
        """\brief return iteration object to receive elements from deals_view
        \param condition - str, part of query after `where` keywork
        \param condargs - list of arguments for query
        \param order_by - list of strings
        """
        q = u'select * from deals_view'
        if not is_null_or_empty(condition):
            q += u' where {0}'.format(condition)
        q += order_by_print(order_by)
        if not is_null_or_empty(condargs):
            return self._sqlite_connection.execute_select(q, condargs)
        else:
            return self._sqlite_connection.execute_select(q)

    def list_positions_view_with_condition(self, condition, condargs, order_by = []):
        """\brief return iteration object to receive elements from positions_view
        \param condition - str, "where" part of query
        \param condargs - list of arguments for query
        \param order_by - list of string, order by construction for
        """
        q = u'select * from positions_view'
        if not is_null_or_empty(condition):
            q += u' where {0}'.format(condition)
        q += order_by_print(order_by)
        if not is_null_or_empty(condargs):
            return self._sqlite_connection.execute_select(q, condargs)
        else:
            return self._sqlite_connection.execute_select(q)


    
    def get_deals_count_range(self, ):
        """\brief return range of min / max of field "count" 
        \return tuple (int - min, int - max)
        """
        rt = self._sqlite_connection.execute("select min(count), max(count) from deals_view").fetchone()
        if rt == (None, None):
            return (0, 0)
        else:
            return rt

    def get_deals_price_range(self, ):
        """\brief return min / max of "points" field from deals_view table
        \return tuple (float, float)
        """
        rt = self._sqlite_connection.execute("select min(points), max(points) from deals_view").fetchone()
        if rt == (None, None):
            return (0, 0)
        else:
            return rt

    def get_deals_commission_range(self, ):
        """\brief return min / max of field commission of deals_view table
        \return tuple (float, float)
        """
        rt = self._sqlite_connection.execute("select min(commission), max(commission) from deals_view").fetchone()
        if rt == (None, None):
            return (0, 0)
        else:
            return rt

    def get_deals_volume_range(self, ):
        """\brief return min / max of field volume of deals_view table
        \return tuple (float, float)
        """
        rt = self._sqlite_connection.execute("select min(volume), max(volume) from deals_view").fetchone()
        if rt == (None, None):
            return (0, 0)
        else:
            return rt

    def get_positions_view_limits(self, limit_name):
        """\brief return low and high limit of the value in positions_view
        \param limit_name - str, name of the field in the positions_view table
        \return tuple, (lower_limit, upper_limit)
        """
        return self._sqlite_connection.execute('select min({0}), max({0}) from positions_view'.format(limit_name)).fetchone()

    def change_point(self, point_id, money_id = None, paper_id = None, point = None, step = None):
        """\brief change existing 'point' record
        \param point_id
        \param money_id
        \param paper_id
        \param point
        \param step
        """
        flds = {}
        for (name, val) in [('money_id', money_id),
                            ('paper_id', paper_id),
                            ('point', point),
                            ('step', step)]:
            if val <> None:
                flds[name] = val
        if len(flds) > 0:
            self._sqlite_connection.update('points', flds, 'id = ?', (point_id, ))
            
    @raise_db_closed
    @in_transaction
    @in_action(lambda self, point_id, *args, **kargs: u'change point record {0}'.format(point_id))
    @pass_to_method(change_point)
    def tachange_point(self, *args, **kargs):
        """\brief wrapper for \ref change_point
        \param point_id
        \param money_id
        \param paper_id
        \param point
        \param step
        """
        pass

    def paper_assigned_deals(self, paper_id):
        """\brief return count of assigned deals for this paper
        \param paper_id - int or str, id of paper object or name
        \exception exceptions.od_exception when paper_id is not found
        """
        paper = self.get_paper(paper_id)
        if paper == None:
            raise od_exception('There is no such "paper" object {0}'.format(paper_id))
        return self._sqlite_connection.execute('select count(*) from deals where paper_id = ?', [paper['id']]).fetchone()[0]

    def load_from_source(self, account_id, source):
        """\brief load deals from source
        \param account_id - int or str, name or id of account
        \param source - \ref sources.common_source instance
        """
        assert(isinstance(source, sources.common_source))
        action_name = source.get_action_name()
        papers = source.receive()
        self.start_transacted_action(action_name)
        acc = self.get_account(account_id)
        if acc == None:
            raise od_exception('There is no such account {0}'.format(account_id))
        try:
            for paper in papers:
                p = self.get_paper(paper['type'], paper['name'])
                if p == None:
                    paper_id = self.create_paper(paper['type'], paper['name'], gethash(paper, 'stock'), gethash(paper, 'class'), gethash(paper, 'full_name'))
                else:
                    paper_id = p['id']
                    
                for deal in paper['deals']:
                    deal['paper_id'] = paper_id
                    try:
                        self.create_deal(acc['id'], deal, False)
                    except sqlite3.IntegrityError:
                        pass
        except Exception as e:
            self.rollback()
            sys.stderr.write(traceback.format_exc())
        else:
            self.recalculate_all_temporary()
            self.commit_transacted_action()
            
    def create_account_in_out(self, account, datetime, money_count, comment = ''):
        """\brief create new account in out object and return its id
        \param account - int or str, id of account or name
        \param datetime - datetime instance
        \param money_count - float, count of money to increase account in (negative value to discard money from the account)
        """
        ac = self.get_account(account)
        if ac == None:
            raise od_exception_parameter_error('There is no such account {0}'.format(account))
        try:
            return self._sqlite_connection.insert('account_in_out', {'account_id' : ac['id'],
                                                                     'datetime' : datetime,
                                                                     'money_count' : money_count,
                                                                     'comment' : comment})
        except sqlite3.IntegrityError as e:
            raise od_exception_db_integrity_error(str(e))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, account, datetime, money_count, *args, **kargs: u'account {0} changed in {1} at {2}'.format(account, money_count, datetime))
    @pass_to_method(create_account_in_out)
    def tacreate_account_in_out(self, *args, **kargs):
        """\brief wrapper around \ref create_account_in_out
        \param account - int or str, id of account or name
        \param datetime - datetime instance
        \param money_count - float, count of money to increase account in (negative value to discard money from the account)
        """
        pass


    def get_account_in_out(self, id_or_account, dtm = None):
        """\brief return object account_in_out by id or by account and dtm
        \param id_or_account - int or str, id of account_in_out or account id or name
        \param dtm - datetime instance or None
        """
        if dtm == None:
            if isinstance(id_or_account, int):
                try:
                    return self._sqlite_connection.execute_select('select * from account_in_out where id = ?', [id_or_account]).fetchone()
                except sqlite3.OperationalError as e:
                    raise od_exception_db_error(str(e))
            else:
                raise od_exception_parameter_error('id_or_account must be int not {0}'.format(type(id_or_account)))
        else:
            if isinstance(dtm, datetime):
                acc = self.get_account(id_or_account)
                if acc == None:
                    raise od_exception_parameter_error('There is no such account {0}'.format(id_or_account))
                try:
                    return self._sqlite_connection.execute_select('select * from account_in_out where account_id = ? and datetime = ?', [acc['id'], dtm]).fetchone()
                except sqlite3.OperationalError as e:
                    raise od_exception_db_error(str(e))
            else:
                raise od_exception_parameter_error('dtm must be datetime instance')
                
    def list_account_in_out(self, account = None, order_by = ['datetime']):
        """\brief list objects of in and out
        \param account - int str or None, if None list for all accounts
        \param order_by
        \return list of hash tables
        """
        q = 'select * from account_in_out'
        if account <> None:
            q += ' where account_id = ?'
        q += order_by_print(order_by)
        try:
            if account == None:
                return self._sqlite_connection.execute_select(q)
            else:
                return self._sqlite_connection.execute_select(q, [account])
        except sqlite3.OperationalError as e:
            raise od_exception_db_error(str(e))
                
    def remove_account_in_out(self, id_or_account, datetime = None):
        """\brief remove account in and out
        \param id_or_account - int or str, if datetime is None then id of object, else id or name of account
        \param datetime - datetime instance or None
        """
        if datetime <> None:
            if isinstance(datetime, datetime):
                acc = self.get_account(id_or_account)
                if acc == None:
                    raise od_exception_parameter_error('There is no such account {0}'.format(id_or_account))
                try:
                    self._sqlite_connection.execute('delete from account_in_out where account_id = ? and datetime = ?',
                                                    [acc['id'], datetime])
                except sqlite3.OperationalError as e:
                    raise od_exception_db_error(str(e))
                except sqlite3.IntegrityError as e:
                    raise od_exception_db_integrity_error(str(e))
            else:
                raise od_exception_parameter_error('datetime must be datetime instance not {0}'.format(type(datetime)))
        else:
            if isinstance(id_or_account):
                try:
                    self._sqlite_connection.execute('delete from account_in_out where id = ?', [id_or_account])
                except sqlite3.OperationalError as e:
                    raise od_exception_db_error(str(e))
                except sqlite3.IntegrityError as e:
                    raise od_exception_db_integrity_error(str(e))
            else:
                raise od_exception_parameter_error('first argument must be int, not {0}'.format(type(id_or_account)))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, id_or_account, datetime = None: ('remove account in out id {0}'.format(id_or_account) if datetime == None else 'remove account in out from acc {0} in {1}'.format(id_or_account, datetime)))
    @pass_to_method(remove_account_in_out)
    def taremove_account_in_out(self, *args, **kargs):
        """\brief wrapper around \ref remove_account_in_out
        \param id_or_account - int or str, if datetime is None then id of object, else id or name of account
        \param datetime - datetime instance or None
        """
        pass
    
