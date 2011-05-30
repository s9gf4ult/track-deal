#!/bin/env python
# -*- coding: utf-8 -*-
## sqlite_model ##

from common_model import common_model
from common_view import common_view
from sconnection import sconnection
from common_methods import *
from exceptions import *
from copy import copy
from datetime import *

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
        Arguments:
        - `parameters`: hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("global_data", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names)))

    @raise_db_closed
    @in_transaction
    @in_action(lambda self, parameters: "add parameters {0}".format(reduce_by_string(", ", paramters.keys())))
    @pass_to_method(add_global_data)
    def taadd_global_data(self, paramters):
        """
        Arguments:
        - `paramters`:
        """
        pass

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
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: "remove global data {0}".format(reduce_by_string(", ", (isinstance(name, basestring) and [name] or name))))
    @pass_to_method(remove_global_data)
    def taremove_global_data(self, name):
        """
        Arguments:
        - `name`:
        """
        pass

    def list_global_data(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from global_data"))

    def add_database_attributes(self, parameters):
        """adds database attributes and
        Arguments:
        - `parameters`: hash with name of parameter and value
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
        Arguments:
        - `name`:
        """
        ret = self._sqlite_connection.execute_select("select value from database_attributes where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

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
    @in_transaction
    @in_action(lambda self, name, *args, **kargs: "remove database attributes {0}".format(reduce_by_string(", ", (isinstance(name, basestring) and [name] or name))))
    @pass_to_method(remove_database_attribute)
    def taremove_database_attribute(self, name):
        """
        Arguments:
        - `name`:
        """
        pass

    def list_database_attributes(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from database_attributes"))
    
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
    @in_transaction
    @in_action(lambda self, type, name, *args, **kargs: "create paper type {0}, name {1}".format(type, name))
    @pass_to_method(create_paper)
    def tacreate_paper(self, *args, **kargs):
        """
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass



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
    @in_transaction
    @in_action(lambda torid, name = None: "remove paper {0}".format((isinstance(torid, int) and "with id {0}".format(torid) or "with type {0} and name {1}".format(torid, name))))
    @pass_to_method(remove_paper)
    def taremove_paper(self, *args, **kargs):
        """
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass


    def list_papers(self, order_by = []):
        """Returns list of papers
        """
        q = "select * from papers"
        if len(order_by) > 0:
            q += "order by {0}".format(reduce_by_string(", ", order_by))
        return self._sqlite_connection.execute_select(q)

    def change_paper(self, paper_id, fields):
        """changes existing paper
        Arguments:
        - `paper_id`:
        - `fields`: hash {"field" : value}
        """
        if len(fields) > 0:
            if self._sqlite_connection.execute("select count(*) from papers where id = ?", [paper_id]).fetchone()[0] > 0:
                remhash(fields, "id")
                self._sqlite_connection.update("papers", fields)
                for (aid, ) in self._sqlite_connection.execute("select distinct account_id from deals where paper_id = ?", [paper_id]):
                    self.recalculate_deals(aid, paper_id)
                for (aid, ) in self._sqlite_connection.execute("select distinct account_id from positions where paper_id = ?", [paper_id]):
                    self.recalculate_positions(aid, paper_id)

    @raise_db_closed
    @in_transaction
    @in_action("change paper")
    @pass_to_method(change_paper)
    def tachange_paper(self, *args, **kargs):
        """
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass


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


    def get_candle(self, candle_id):
        """Get candle by id
        Arguments:
        - `candle_id`:
        """
        ret = self._sqlite_connection.execute_select("select * from candles where id = ?", [candle_id]).fetchall()
        return (len(ret) > 0 and ret[0] or None)

    @remover_decorator("candles", {int : "id"})
    def remove_candle(self, candles_id):
        """removes one or more candles
        Arguments:
        - `candles_id`: int or list of ints
        """
        pass

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


    def create_money(self, name, full_name = None):
        """Creates new money and return it's id
        Arguments:
        - `name`:
        - `full_name`:
        """
        return self._sqlite_connection.insert("moneys", {"name" : name,
                                                         "full_name" : full_name}).lastrowid

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

    @remover_decorator("moneys", {int : "id", basestring : "name"})
    def remove_money(self, name_or_id):
        """Removes money by name or by id
        Arguments:
        - `name_or_id`:
        """
        pass

    def list_moneys(self, order_by = []):
        """return list of moneys
        """
        q = "select * from moneys{0}".format((len(order_by) > 0 and " order by {0}".format(reduce_by_string(", ", order_by))  or ""))
        return self._sqlite_connection.execute_select(q)
    
    def create_point(self, paper_id, money_id, point, step):
        """Creates point explanation and return it's id
        Arguments:
        - `paper_id`:
        - `money_id`:
        - `point`:
        - `step`:
        """
        ret = self._sqlite_connection.insert("points", {"paper_id" : paper_id, "money_id" : money_id, "point" : point, "step" : step}).lastrowid
        for (aid, ) in self._sqlite_connection.execute("select id from accounts where money_id = ?", [money_id]):
            self.recalculate_deals(aid, paper_id)
            self.recalculate_positions(aid, paper_id)

    @raise_db_closed
    @in_transaction
    @in_action(lambda paper_id, money_id, *args, **kargs: "create point for paper {0} and money {1}".format(paper_id, money_id))
    @pass_to_method(create_point)
    def tacreate_point(self, *args, **kargs):
        """transacted wrapper for create point
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass

    
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

    def remove_point(self, id_or_paper_id, money_id = None):
        """Removes point of this paper / money or by id
        Arguments:
        - `id_or_paper_id`:
        - `money_id`:
        """
        if money_id != None:
            self._sqlite_connection.execute("delete from points where paper_id = ? and money_id = ?", [id_or_paper_id, money_id])
            for (aid, ) in self._sqlite_connection.execute("select id from accounts where money_id = ?", [money_id]):
                self.recalculate_deals(aid, id_or_paper_id)
                self.recalculate_positions(aid, id_or_paper_id)
        else:
            self._sqlite_connection.execute("delete from points where id = ?", [id_or_paper_id])
            (paid, ) = self._sqlite_connection.execute("select paper_id from points where id = ?", [id_or_paper_id]).fetchone() or (None)
            if paid <> None:
                for (aid, ) in self._sqlite_connection.execute("select a.id from accounts a inner join points p on p.money_id = a.money_id where p.id = ?", [id_or_paper_id]):
                    self.recalculate_deals(aid, paid)
                    self.recalculate_positions(aid, paid)

    @raise_db_closed
    @in_transaction
    @in_action(lambda id_or_paper_id, money_id = None:"remove point {0}".format((money_id == None and "with id {0}".format(id_or_paper_id) or "with paper_id {0} and money_id {1}".format(id_or_paper_id, money_id))))
    @pass_to_method(remove_point)
    def taremove_point(self, *args, **kargs):
        """transacted wrapper for remove point
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass




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
        aid = self._sqlite_connection.insert("accounts", {"name" : name, "comments" : comment, "money_id" : mid, "money_count" : money_count}).lastrowid
        if self.get_global_data("current_account") == None and self._sqlite_connection.execute("select count(*) from accounts").fetchone()[0] == 1:
            self.add_global_data({"current_account" : aid})
        return aid

    @raise_db_closed
    @in_transaction
    @in_action(lambda name, *args, **kargs: u"create account {0}".format(name))
    @pass_to_method(create_account)
    def tacreate_account(self, *args, **kargs):
        """transacted wrapper for create account
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass


    def change_account(self, aid, money_id_or_name = None, money_count = None, comment = None):
        """changes existing account
        Arguments:
        - `aid`:
        - `money_id_or_name`:
        - `money_count`:
        - `comment`:
        """
        sets = {}
        if money_id_or_name != None:
            m = self.get_money(money_id_or_name)
            sets["money_id"] = m["id"]
        if money_count != None:
            sets["money_count"] = money_count
        if comment != None:
            sets["comments"] = comment
        if len(sets) > 0:
            self._sqlite_connection.update("accounts", sets, "id = ?", [aid])

        if money_id_or_name <> None or money_count <> None:
            for (paid, ) in self._sqlite_connection.execute("select distinct paper_id from deals where account_id = ?", [aid]):
                self.recalculate_deals(aid, paid)

            for (paid, ) in self._sqlite_connection.execute("select distinct paper_id from positions where account_id = ?", [aid]):
                self.recalculate_positions(aid, paid)

    @raise_db_closed
    @in_transaction
    @in_action(lambda aid, *args, **kargs: "changed account with id {0}".format(aid))
    @pass_to_method(change_account)
    def tachange_account(self, *args, **kargs):
        """transacted wrapper for change account function
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass

    def list_accounts(self, order_by = []):
        """Return list of accounts
        """
        return self._sqlite_connection.execute_select("select * from accounts{0}".format(order_by_print(order_by)))

    @remover_decorator("accounts", {int : "id", basestring : "name"})
    def remove_account(self, name_or_id):
        """Removes account by name or by id
        Arguments:
        - `name_or_id`:
        """
        pass

    @raise_db_closed
    @in_transaction
    @in_action(lambda name_or_id: "remove account with {0}".format((isinstance(name_or_id, int) and "id {0}".format(name_or_id) or "name {0}".format(name_or_id))))
    @pass_to_method(remove_account)
    def taremove_account(self, *args, **kargs):
        """transacted wrapper for remove account
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass


    def get_account(self, aid):
        """
        Arguments:
        - `aid`:
        """
        aa = self._sqlite_connection.execute_select("select * from accounts where id = ?", [aid]).fetchall()
        if len(aa) > 0:
            return aa[0]
        else:
            return None

            
    def create_deal(self, account_id, deal):
        """creates one or more deal with attributes, return id of last created
        Arguments:
        - `account_id`:
        - `deal`: list of or one hash table with deal
        """
        did = None
        deals = (isinstance(deal, dict) and [deal] or deal)
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
            did = self._sqlite_connection.insert("deals", dd).lastrowid
            if len(uat) > 0:
                uk = uat.keys()
                uv = map(lambda k: uat[k], uk)
                self._sqlite_connection.executemany("insert into user_deal_attributes(deal_id, name, value) values (?, ?, ?)", map(lambda name, value: (did, name, value), uk, uv)) 
            if len(sat) > 0:
                sk = sat.keys()
                sv = map(lambda k: sat[k], sk)
                self._sqlite_connection.executemany("insert into stored_deal_attributes(deal_id, type, value) values (?, ?, ?)", map(lambda typ, val: (did, typ, val), sk, sv))
        md = reduce(lambda a, b: (a["datetime"] < b["datetime"] and a or b), deals)
        self.recalculate_deals(account_id, md["paper_id"], md["id"])
        return did

    @raise_db_closed
    @in_transaction
    @in_action(lambda account_id, deal, *args, **kargs: "create deal for paper {0}".format(deal["paper_id"]))
    @pass_to_method(create_deal)
    def tacreate_deal(self, *args, **kargs):
        """wrapper for create deal
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass


    def list_deals(self, account_id = None, paper_id = None, order_by = []):
        """Return cursor iterating on deals
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `order_by`:
        """
        conds = []
        if account_id != None:
            conds.append(("=", ["account_id"], account_id))
        if paper_id != None:
            conds.append(("=", ["paper_id"], paper_id))
        return self._sqlite_connection.execute_select_cond("deals", wheres = conds, order_by = order_by)
        
    def remove_deal(self, deal_id):
        """remove one or more deal by id
        Arguments:
        - `deal_id`:
        """
        x = map(lambda a: (a, ), (isinstance(deal_id, int) and [deal_id] or deal_id))
        self._sqlite_connection.executemany("delete from deals where id = ?", x)
        self._sqlite_connection.executemany("delete from deals_view where deal_id = ?", x)
        self.fix_groups()
        self.fix_positions()

    def fix_groups(self, ):
        """fixes broken groups by deleting
        """
        self._sqlite_connection.execute("""delete from deal_groups where id in (
        select id from (
        select g.group_id as id, count(d.id) as count
        from deal_group_assign g left join deals d on g.deal_id = d.id
        group by g.group_id)
        where count = 0

        union

        select g.id from deal_groups g
        where not exists(select * from deal_group_assign where gorup_id = g.id)

        union

        select id from (
        select g.group_id as id, sum(d.count * d.direction) as sum
        from deal_group_assign g left join deals d on g.deal_id = g.id
        group by g.group_id)
        where sum <> 0)""")

    def fix_positions(self, ):
        """fixes broken positions by deleting
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
    @in_action(lambda *args, **kargs: "remove deals(s)")
    @pass_to_method(remove_deal)
    def taremove_deal(self, *args, **kargs):
        """
        Arguments:
        - `*args`:
        - `**kargs`:
        """
        pass

    def get_user_deal_attributes(self, deal_id):
        """return hash of attributes
        Arguments:
        - `deal_id`:
        """
        ret = {}
        for at in self._sqlite_connection.execute_select_cond("user_deal_attributes", wheres = [("=", ["deal_id"], deal_id)]):
            ret[at["name"]] = at["value"]
        return ret

    def get_stored_deal_attributes(self, deal_id):
        """return hash of stored attributes
        
        Arguments:
        - `deal_id`:
        """
        ret = {}
        for at in self._sqlite_connection.execute_select_cond("stored_deal_attributes", wheres = [("=", ["deal_id"], deal_id)]):
            ret[at["type"]] = at["value"]
        return ret

    def create_position(self, open_group_id, close_group_id, user_attributes = {}, stored_attributes = {}, manual_made = None, do_not_delete = None):
        """Return position id built from groups
        Arguments:
        - `open_group_id`:
        - `close_group_id`:
        """
        for field in ["paper_id", "account_id"]:
            odids = self._sqlite_connection.execute("select count(*) from (select distinct d.{0} from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on dg.group_id = g.id where g.id = ? or g.id = ?)".format(field), [open_group_id, close_group_id]).fetchone()[0]
            assert(odids == 1)

        odirs = map(lambda a: self._sqlite_connection.execute("select distinct d.direction from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ?", [a]).fetchall(), [open_group_id, close_group_id])
        assert(len(odirs[0]) == len(odirs[1]) == 1)
        assert(odirs[0][0][0] == -(odirs[1][0][0]) <> 0)
        cnts = map(lambda a: self._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [a]).fetchone()[0], [open_group_id, close_group_id])
        assert(cnts[0] == cnts[1] > 0)
        dds = self._sqlite_connection.execute("select max(d.datetime), min(dd.datetime) from deals d inner join deal_group_assign dg on dg.deal_id = d.id, deals dd inner join deal_group_assign ddg on ddg.deal_id = dd.id where dg.group_id = ? and ddg.group_id = ?", [open_group_id, close_group_id]).fetchone()
        assert(dds[0] <= dds[1])
        (apids, ) = self._sqlite_connection.execute("select count(*) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where (dg.group_id = ? or dg.group_id = ?) and d.position_id is not null", [open_group_id, close_group_id]).fetchone()
        assert(apids == 0)
        (acc_id, pap_id) = self._sqlite_connection.execute("select d.account_id, d.paper_id from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? limit 1", [open_group_id]).fetchone()
        (comm, ) = self._sqlite_connection.execute("select sum(d.commission) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? or dg.group_id = ?", [open_group_id, close_group_id]).fetchone()
        (odate, opoints) = self._sqlite_connection.execute("select max(d.datetime), sum(d.points * d.count) / sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [open_group_id]).fetchone()
        (cdate, cpoints) = self._sqlite_connection.execute("select max(d.datetime), sum(d.points * d.count) / sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [close_group_id]).fetchone()
        pid = self._sqlite_connection.insert("positions", {"account_id" : acc_id,
                                                           "paper_id" : pap_id,
                                                           "count" : cnts[0],
                                                           "direction" : odirs[0][0][0],
                                                           "commission" : comm,
                                                           "open_datetime" : odate,
                                                           "close_datetime" : cdate,
                                                           "open_points" : opoints,
                                                           "close_points" : cpoints,
                                                           "manual_made" : manual_made,
                                                           "do_not_delete" : do_not_delete}).lastrowid
        self._sqlite_connection.execute("update deals set position_id = ? where id in (select dg.deal_id from deal_group_assign dg where dg.group_id = ? or dg.group_id = ?)", [pid, open_group_id, close_group_id])
        uk = user_attributes.keys()
        if len(uk) > 0:
            self._sqlite_connection.insert("user_position_attributes", map(lambda k: {"name" : k, "value" : user_attributes[k], "position_id" : pid}, uk))
        sk = stored_attributes.keys()
        if len(sk) > 0:
            self._sqlite_connection.insert("stored_position_attributes", map(lambda k: {"type" : k, "value" : stored_attributes[k], "position_id" : pid}, sk))
        self.recalculate_positions(acc_id, pap_id, pid)
        return pid

    def list_positions(self, account_id = None, paper_id = None, order_by = []):
        """return cursor for getting position descriptions
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `order_by`:
        """
        conds = []
        if account_id <> None:
            conds.append(("=", ["account_id"], account_id))
        if paper_id <> None:
            conds.append(("=", ["paper_id"], paper_id))
        return self._sqlite_connection.execute_select_cond("positions", wheres = conds, order_by = order_by)
                          
    
    def get_position_user_attributes(self, position_id, order_by = []):
        """return cursor for user position attributes
        Arguments:
        - `position_id`:
        """
        return self._sqlite_connection.execute_select_cond("user_position_attributes", wheres = [("=", ["position_id"], position_id)], order_by = order_by)
                                                                                                 
    def get_stored_position_attributes(self, position_id, order_by = []):
        """return cursor for stcored position attributes
        Arguments:
        - `position_id`:
        - `order_by`:
        """
        return self._sqlite_connection.execute_select_cond("stored_position_attributes", wheres = [("=", ["position_id"], position_id)], order_by = order_by)

    def create_group(self, deal_id):
        """return id the group maked from deals
        Arguments:
        - `deal_id`: int or list of ints
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
                                                                     "direction" : direction}).lastrowid
            else:
                assert(paper_id == deal["paper_id"])
                assert(direction == deal["direction"])
                assert(account_id == deal["account_id"])
            self._sqlite_connection.insert("deal_group_assign", {"deal_id" : did, "group_id" : gid})
        return gid

    def add_to_group(self, group_id, deal_id):
        """add deals to group
        Arguments:
        - `group_id`:
        - `deal_id`:
        """
        g = self._sqlite_connection.execute_select("select * from deal_groups where id = ?", [group_id]).fetchall()[0]
        for di in (isinstance(deal_id, int) and [deal_id] or deal_id):
            (c,) = self._sqlite_connection.execute("select count(*) from deals where id = ? and paper_id = ? and direction = ? and account_id = ?", [di, g["paper_id"], g["direction"], g["account_id"]]).fetchone()
            assert(c == 1)
            self._sqlite_connection.insert("deal_group_assign", {"group_id" : group_id,
                                                                 "deal_id" : di})
            

            
    def calculate_deals(self, account_id, paper_id, deal_id = None):
        """Recalculate temporary table deals_view starting from deal_id 
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `deal_id`:
        """
        if deal_id == None:
            cur = self._sqlite_connection.execute_select("select d.* from deals d where d.account_id = ? and d.paper_id = ?  and not exists(select dd.* from deals dd where dd.parent_deal_id = d.id) order by d.datetime", [account_id, paper_id])
            (mc, ) = self._sqlite_connection.execute("select a.money_count from accounts a where a.id = ?", [account_id]).fetchone()
            self._calculate_deals_with_initial(cur, mc, 0)
        else:
            cur = self._sqlite_connection.execute_select("select d.* from deals d, deals dd where dd.id = ? and d.datetime >= dd.datetime and d.account_id = ? and d.paper_id = ? and not exists(select ddd.* from deals ddd where ddd.parent_deal_id = d.id) order by d.datetime", [deal_id, account_id, paper_id])
            (mc, pbl) = self._sqlite_connection.execute("select dw.net_after, dw.paper_ballance_after from deals_view dw inner join deals d on dw.deal_id = d.id where d.id = ?", [deal_id]).fetchone() or (None, None)
            if mc == None:
                return self.calculate_deals(account_id, paper_id)
            self._calculate_deals_with_initial(cur, mc, pbl)
                                     
    def _calculate_deals_with_initial(self, cursor, money, paper_ballance):
        """calculates deals given in cursor
        Arguments:
        - `cursor`:
        - `money`:
        - `paper_ballance`:
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
            
        first = True
        for dd in cursor:
            if first:
                common = self._sqlite_connection.execute_select("select p.id as paper_id, p.type as paper_type, p.class as paper_class, p.name as paper_name, m.id as money_id, m.name as money_name from accounts a inner join deals d on d.account_id = a.id inner join moneys m on m.id = a.money_id inner join papers p on d.paper_id = p.id where d.id = ?", [dd["id"]]).fetchall()[0]
                (common["point"], common["step"]) = self._sqlite_connection.execute("select point, step from points where paper_id = ? and money_id = ?", [common["paper_id"], common["money_id"]]).fetchone() or (1, 1)
            newdw = copy(dd)
            del newdw["id"]
            del newdw["sha1"]
            del newdw["parent_deal_id"]
            del newdw["position_id"]
            newdw["deal_id"] = dd["id"]
            add_hash(newdw, common)
            if first:
                addition(newdw, money, paper_ballance)
            else:
                addition(newdw, olddw["net_after"], olddw["paper_ballance_after"])
            self._sqlite_connection.insert("deals_view", newdw)
            olddw = newdw
            first = False

    def recalculate_deals(self, account_id, paper_id, deal_id = None):
        """removes and recalculate additional table for deals
        Arguments:
        - `account_id`:
        - `paper_id`:
        """
        if deal_id == None:
            self._sqlite_connection.execute("delete from deals_view where account_id = ? and paper_id = ?", [account_id, paper_id])
            self._sqlite_connection.execute("delete from deals_view where id in (select dw.id from deals_view dw inner join deals d on dw.deal_id = d.id where d.account_id = ? and d.paper_id = ?)", [account_id, paper_id])
            self.calculate_deals(account_id, paper_id)
        else:
            self._sqlite_connection.execute("delete from deals_view where id in (select dv.id from deals_view dv inner join deals d on dv.deal_id = d.id, deals dd where dd.id = ? and d.account_id = ? and d.paper_id = ? and d.datetime >= dd.datetime)", [deal_id, account_id, paper_id])
            self.calculate_deals(account_id, paper_id, deal_id)

    def __recalculate_deals__(self, account_id, paper_id, *args, **kargs):
        """
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `*args`:
        - `**kargs`:
        """
        self.recalculate_deals(account_id, paper_id)


    def make_groups(self, account_id, paper_id, time_distance = 5):
        """
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `time_distance`:max time difference between deals in one group
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
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `time_distance`:
        """
        self._sqlite_connection.execute("delete from deal_groups where id in (select distinct g.id from deal_groups g inner join deal_group_assign dg on dg.group_id = g.id inner join deals d on dg.deal_id = d.id where d.account_id = ? and d.paper_id = ?)", [account_id, paper_id])
        self._sqlite_connection.execute("delete from deal_groups where account_id = ? and paper_id = ?", [account_id, paper_id])
        self.make_groups(account_id, paper_id, time_distance)
                
    def list_groups(self, account_id, paper_id):
        """
        Arguments:
        - `account_id`:
        - `paper_id`:
        """
        return self._sqlite_connection.execute_select("select g.* from deal_groups g inner join deal_group_assign dg on dg.group_id = g.id inner join deals d on dg.deal_id = d.id  where d.account_id = ? and d.paper_id = ? group by g.id", [account_id, paper_id])

    
    def __remake_groups__(self, account_id, paper_id, time_distance = 5, *args, **kargs):
        """
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `time_distance`:
        - `*args`:
        - `**kargs`:
        """
        self.remake_groups(account_id, paper_id, time_distance)

    def make_positions(self, account_id, paper_id, time_distance = 5):
        """automatically makes positions
        Arguments:
        - `account_id`:
        - `paper_id`:
        - `time_distance`: time distance for make_groups
        """
        self.remake_groups(account_id, paper_id, time_distance)
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
            self.create_position(g1, g2)
            self._sqlite_connection.executemany("delete from deal_groups where id = ?", [(g1,), (g2,)])
            return True
        while go_on():
            pass

    def try_make_ballanced_groups(self, gid1, gid2):
        """if count of papers for gid1 and gid2 is the same then just return gid1 and gid2,
        else just split gid1 or gid2 to the minimal count papers and return splited gids
        Arguments:
        - `gid1`: group_id
        - `gid2`:
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

    def __recalculate_deals_by_group_id__(self, gid, *args, **kargs):
        """
        Arguments:
        - `gid`:
        - `*args`:
        - `**kargs`:
        """
        (account_id, paper_id) = self._sqlite_connection.execute("select account_id, paper_id from deal_groups where id = ?", [gid]).fetchone()
        self.recalculate_deals(account_id, paper_id)


    def split_group(self, gid, count):
        """return tuple (gid1, gid2)
        if count >= sum of counts all deals assigned to group `gid` then gid2 = None
        Arguments:
        - `gid`: Group id split to
        - `count`: count of papers of papers assigned to gid1
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
        Arguments:
        - `gid`:
        - `deal_id`:
        """
        deals = map(lambda a: (a,), (isinstance(deal_id, int) and [deal_id] or deal_id))
        self._sqlite_connection.executemany("delete from deal_group_assign where deal_id = ?", deals)


    def __recalculate_deals_by_id__(self, deal_id, *args, **kargs):
        """get account_id and paper_id from deal and pass to __recalculate_deals__
        Arguments:
        - `deal_id`:
        - `*args`:
        - `**kargs`:
        """
        (aid, paid) = self._sqlite_connection.execute("select account_id, paper_id from deals where id = ?", [deal_id]).fetchone()
        self.__recalculate_deals__(aid, paid)

    def split_deal(self, deal_id, count):
        """return tuple with 2 deal_id. One is the deal with `count` papers, second with remainder
        if count of deal is less or equal to `count` then return tuple (deal_id, None)
        Arguments:
        - `deal_id`:
        - `count`: needed count of papers for deal
        """
        deal = self._sqlite_connection.execute_select("select * from deals where id = ?",[deal_id]).fetchall()[0]
        if count >= deal["count"]:
            return (deal["id"], None)
        else:
            nd1 = copy(deal)
            del nd1["id"]
            nd1["parent_deal_id"] = deal["id"]
            nd2 = copy(nd1)
            nd1["count"] = count
            nd2["count"] = deal["count"] - count
            d1 = self.create_deal(deal["account_id"], nd1)
            d2 = self.create_deal(deal["account_id"], nd2)
            (pap, mon) = self._sqlite_connection.execute("select paper_ballance_before, net_before from deals_view where deal_id = ?", [deal["id"]]).fetchone()
            self._sqlite_connection.execute("delete from deals_view where deal_id = ?", [deal["id"]])
            self._calculate_deals_with_initial(self._sqlite_connection.execute_select("select * from deals where id = ? or id = ?",[d1, d2]), mon, pap)
            return (d1, d2)
            

    def start_action(self, action_name):
        """starts new action with an action name
        Arguments:
        - `action_name`:
        """
        ab = self._sqlite_connection.execute("select count(h1.id) from hystory_steps h1, current_hystory_position ch where h1.id > ch.step_id").fetchone()[0]
        if ab > 0:
            raise od_exception_action_cannot_create(ab)
        aid = self._sqlite_connection.insert("hystory_steps", {"autoname" : action_name,
                                                               "datetime" : datetime.now()}).lastrowid
        self._sqlite_connection.insert("current_hystory_position", {"step_id" : aid})
        
    def end_action(self, ):
        """ends an action recording
        """
        self._sqlite_connection.execute("delete from current_hystory_position")

    def list_actions(self, ):
        """list all actions executed
        """
        return self._sqlite_connection.execute_select("select * from hystory_steps")

    def get_current_action(self, ):
        """return current action or None if no one set
        """
        a = self._sqlite_connection.execute_select("select h.* from hystory_steps h inner join current_hystory_position c on c.step_id = h.id").fetchall()
        if len(a) > 0:
            return a[0]
        else:
            return None
        
    def calculate_positions(self, aid, paid, pid = None):
        """
        Arguments:
        - `aid`:
        - `paid`:
        - `pid`:
        """
        if pid == None:
            cur = self._sqlite_connection.execute_select("select * from positions order by close_datetime, open_datetime")
            net = self.get_account(aid)["money_count"]
            self._calculate_positions_with_initial(cur, net, net)
        else:
            cur = self._sqlite_connection.execute_select("select p.* from positions p, positions pp where pp.id = ? and p.close_datetime >= pp.close_datetime order by close_datetime, open_datetime",[pid])
            (net, gross) = self._sqlite_connection.execute("select net_after, gross_after from positions_view where position_id = ?", [pid]).fetchone() or (None, None)
            if net == gross == None:
                return self.recalculate_positions(aid, paid)
            self._calculate_positions_with_initial(cur, net, gross)

    def _calculate_positions_with_initial(self, cursor, net, gross):
        """
        Arguments:
        - `cursor`:
        - `net`: net start from
        - `gross`: gross start from
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
            post["steps_range"] = post["points_range"] / post["step"]
            post["steps_range_abs"] = abs(post["steps_range"])
            post["steps_range_abs_formated"] = format_abs_value(post["steps_range"])
            post["percent_range"] = post["pl_net"] / netx * 100
            post["percent_range_abs"] = abs(post["percent_range"])
            post["percent_range_abs_formated"] = format_abs_value(post["percent_range"])
            post["net_before"] = netx
            post["net_after"] = netx + post["pl_net"]
            post["gross_before"] = grossx
            post["gross_after"] = grossx + post["pl_gross"]
          
        
        first = True
        for pos in cursor:
            posx = copy(pos)
            del posx["id"]
            posx["position_id"] = pos["id"]
            if first:
                common = {}
                (paper_id, ) = self._sqlite_connection.execute("select paper_id from positions where id = ? limit 1", [pos["id"]]).fetchone()
                (common["money_id"], common["money_name"]) = self._sqlite_connection.execute("select m.id, m.name from moneys m inner join accounts a on a.money_id = m.id where a.id = ? limit 1", [pos["account_id"]]).fetchone()
                (common["point"], common["step"]) = self._sqlite_connection.execute("select point, step from points where money_id = ? and paper_id = ?", [common["money_id"], paper_id]).fetchone() or (1, 1)
                (common["paper_type"], common["paper_stock"], common["paper_class"], common["paper_name"]) = self._sqlite_connection.execute("select type, stock, class, name from papers where id = ?", [paper_id]).fetchone()
            add_hash(posx, common)
            if first:
                do_the_work(posx, net, gross)
            else:
                do_the_work(posx, oldpos["net_after"], oldpos["gross_after"])
            self._sqlite_connection.insert("positions_view", posx)
            oldpos = posx
            first = False
            

    def recalculate_positions(self, aid, paid, position_id = None):
        """
        Arguments:
        - `aid`: account id
        - `paid`: paper id
        - `position_id`: id of position recalculate from
        """
        if position_id == None:
            self._sqlite_connection.execute("delete from positions_view where account_id = ? and paper_id = ?", [aid, paid])
            self._sqlite_connection.execute("delete from positions_view where id in (select pw.id from positions_view pw inner join positions p on p.id = pw.position_id where p.account_id = ? and p.paper_id = ?)",[aid, paid])
            self.calculate_positions(aid, paid)
        else:
            self._sqlite_connection.execute("delete from positions_view where id in (select pv.id from positions_view pv inner join positions p on pv.position_id = p.id, positions pp where pp.id = ? and ((p.account_id = ? and p.paper_id = ?) or (pv.account_id = ? and pv.paper_id = ?)) and p.close_datetime >= pp.close_datetime)", [position_id, aid, paid, aid, paid])
            self.calculate_positions(aid, paid, position_id)


