#!/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import time
import datetime
import re
from copy import copy
from common_methods import *
from math import *

class string_aggregate:
    ret = None
    def step(self, value):
        if self.ret == None:
            self.ret = value
        else:
            self.ret = u'{0}; {1}'.format(self.ret, value)
            
    def finalize(self):
        return self.ret

def attr_name_val(name, value):
    if is_null_or_empty(name) and is_null_or_empty(value):
        return None
    elif is_null_or_empty(value):
        return name
    elif is_null_or_empty(name):
        raise Exception("if value is not null name can not be null")
    else:
        return u'{0} = {1}'.format(name, value)

def get_date(val):
    dt = datetime.datetime.fromtimestamp(val)
    date = time.mktime(dt.date().timetuple())
    return date

def format_date(val):
    dt = datetime.datetime.fromtimestamp(val)
    return dt.date().__str__()

def get_time(val):
    dt = datetime.datetime.fromtimestamp(val)
    ttt = dt.second + dt.minute * 60 + dt.hour * 3600
    return ttt

def format_time(val):
    hours = trunc(val / 3600)
    val = val % 3600
    minutes = trunc(val / 60)
    seconds = trunc(val % 60)
    return u'{0:02}:{1:02}:{2:02}'.format(hours, minutes, seconds)

def get_day_of_week(val):
    dt = datetime.datetime.fromtimestamp(val)
    return dt.weekday()

def buy_sell(val):
    return val < 0 and u'B' or 'S'

def format_time_distance(val):
    days = trunc(val / (24 * 3600))
    val = val % (24 * 3600)
    ret = ""
    if days > 0:
        ret += u'{0}d '.format(days)
    ret += format_time(val)
    return ret
        

def short_long(val):
    return val < 0 and u'LONG' or 'SHORT'

def minus_brakets(val):
    if val < 0:
        return u'({0})'.format(abs(val))
    else:
        return u'{0}'.format(val)
    

class deals_proc():
    _total_changes = None
    last_total_changes = 0
    connection = None
    current_user_version = 2
    
    def __init__(self):
        sqlite3.register_adapter(str, lambda a: a.decode(u'utf-8'))
        sqlite3.register_adapter(datetime.datetime, lambda a: time.mktime(a.timetuple()))
        sqlite3.register_adapter(datetime.date, lambda a: time.mktime(a.timetuple()))
        sqlite3.register_adapter(datetime.time, lambda a: a.hour * 3600 + a.minute * 60 + a.second)
        sqlite3.register_converter('datetime', lambda a: datetime.datetime.fromtimestamp(float(a)))

        
    def create_temporary_tables(self):
        self.connection.execute("create temporary table selected_stocks (id integer primary key not null, stock text not null, unique(stock))")
        self.connection.execute("create temporary table pselected_stocks (id integer primary key not null, stock text not null, unique(stock))")
        self.connection.execute("create temporary table selected_accounts (id integer primary key not null, account_id integer not null, unique(account_id))")
        self.connection.execute("create temporary table pselected_accounts (id integer primary key not null, account_id integer not null, unique(account_id))")
        self.connection.execute("create temporary view accounts_view as select a.id, a.name, a.currency, a.first_money, count(d.id) as deals_count, (case count(d.id) when 0 then a.first_money else a.first_money + sum(d.deal_sign * d.volume) - sum(d.broker_comm + d.stock_comm) end) as last_money from accounts a left join deals d on d.account_id = a.id where d.not_actual is null group by a.id")
        self.connection.execute("create temporary view deals_view as select d.id, d.datetime, get_date(d.datetime) as date, format_date(get_date(d.datetime)) as formated_date, format_time(get_time(d.datetime)) as formated_time, get_time(d.datetime) as time, get_day_of_week(d.datetime) as day_of_week, d.security_name, d.security_type, d.quantity, d.price, d.deal_sign, buy_sell(d.deal_sign) as buy_sell_formated, d.volume, d.broker_comm, d.stock_comm, d.broker_comm + d.stock_comm as comm, reduce_string(name_value(a.name, a.value)) as attributes, d.account_id, d.position_id, d.parent_deal_id from deals d left join deal_attributes a on a.deal_id = d.id where d.not_actual is null group by d.id")

        self.connection.execute("""create temporary table internal_position_attributes
        (id integer primary key not null,
        position_id integer not null,
        account_id integer,
        net_before float,
        net_after float,
        gross_before float,
        gross_after float,
        comm_before float,
        comm_after float,
        plnet_acc float,
        unique(position_id))""")
        
        self.connection.execute("""
        create temporary view positions_view as select
        p.id, p.open_datetime, p.close_datetime, p.ticket as ticket, p.count as count, p.direction as direction, short_long(p.direction) as direction_formated,
        get_date(p.open_datetime) as open_date, format_date(get_date(p.open_datetime)) as open_date_formated,
        get_time(p.open_datetime) as open_time, format_time(get_time(p.open_datetime)) as open_time_formated,
        get_date(p.close_datetime) as close_date, format_date(get_date(p.close_datetime)) as close_date_formated,
        get_time(p.close_datetime) as close_time, format_time(get_time(p.close_datetime)) as close_time_formated,
        p.open_coast, p.close_coast, ((p.open_coast + p.close_coast) / 2) as coast,
        p.open_volume, p.close_volume, ((p.open_volume + p.close_volume) / 2) as volume,
        abs(i.plnet_acc) as plnet_acc, minus_brakets(i.plnet_acc) as plnet_acc_formated, abs(p.pl_net / p.open_volume * 100) as plnet_volume,
        abs((p.stock_comm + p.broker_comm) / p.pl_gross) as comm_pl_gross,
        abs(p.open_coast - p.close_coast) as coast_range, minus_brakets((p.open_coast - p.close_coast) * p.direction) as coast_range_formated, abs(p.pl_gross) as pl_gross_range, minus_brakets(p.pl_gross) as pl_gross_range_formated, minus_brakets(p.pl_net) as pl_net_range_formated,
        abs(p.pl_net) as pl_net_range, (p.stock_comm + p.broker_comm) as comm, (case when p.pl_net > 0 then 'PROFIT' else 'LOSS' end) as profit_loss, (case when p.pl_net >= 0 then 1 else -1 end) as profit, (p.close_datetime - p.open_datetime) as duration, format_time_distance(p.close_datetime - p.open_datetime) as formated_duration,
        i.net_before as net_before, i.net_after as net_after, i.gross_before as gross_before, i.gross_after as gross_after,
        i.comm_before as comm_before, i.comm_after as comm_after, i.account_id as account_id
        from positions p left join internal_position_attributes i on i.position_id = p.id""")
        
    def get_count_deals_in_account(self, account_id):
        return self.connection.execute("select count(*) from deals where account_id = ? and not_actual is null", (account_id, )).fetchone()[0]

    def get_count_positions_in_account(self, account_id):
        return self.connection.execute("select count(*) from (select distinct position_id from deals where account_id = ? and not_actual is null)",(account_id, )).fetchone()[0]

    def get_account_name_by_id(self, account_id):
        return self.connection.execute("select name from accounts where id = ? limit 1", (account_id, )).fetchone()[0]

    def open(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename, detect_types = sqlite3.PARSE_DECLTYPES)
        self.last_total_changes = self.connection.total_changes
        self.connection.execute("pragma foreign_keys=on")
        self.connection.execute("begin transaction")
        self.connection.create_aggregate("reduce_string", 1, string_aggregate)
        self.connection.create_function("name_value", 2, attr_name_val)
        self.connection.create_function("get_date", 1, get_date)
        self.connection.create_function("get_time", 1, get_time)
        self.connection.create_function("format_date", 1, format_date)
        self.connection.create_function("format_time", 1, format_time)
        self.connection.create_function("get_day_of_week", 1, get_day_of_week)
        self.connection.create_function("short_long", 1, short_long)
        self.connection.create_function("buy_sell", 1, buy_sell)
        self.connection.create_function("format_time_distance", 1, format_time_distance)
        self.connection.create_function("minus_brakets", 1, minus_brakets)
            

    def open_existing(self, filename):
        self.open(filename)
        self.create_temporary_tables()
        (cuv, ) = self.connection.execute("pragma user_version").fetchone()
        if cuv != self.current_user_version:
            raise Exception(u'Не совпадает версия базы, должна быть {0}, а в базе {1}'.format(self.current_user_version, cuv))
        self.check_database_version_2()
        self.recalculate_temporary_attributes()
        self.commit()

    def recalculate_temporary_attributes(self):
        for (acc_id, ) in self.connection.execute("select id from accounts"):
            self.recalculate_position_attributes(acc_id)
    

    def check_tables_existance(self, tables):
        etables = map(lambda a: a[0].decode('utf-8'), self.connection.execute("select name from sqlite_master where type = 'table'"))
        if set(etables) != set(tables):
            raise Exception(u'Должны существовать такие таблицы {0}, а существуют такие {1}'.format(etables, tables))

    def check_table_structure(self, table, fields):
        """`fields' is a list of tuples [(name_field, type_field, not_nullable, is_primary_key)]"""
        efields = map(lambda a: (a[1].decode('utf-8'), a[2].decode('utf-8'), a[3].decode('utf-8'), a[5].decode('utf-8')), self.connection.execute("pragma table_info(?)", table))
        ffields = map(lambda a: tuple(map(lambda x: x.decode('utf-8'), a)), fields)
        if set(efields) != set(ffields):
            raise Exception(u'В таблице {0} должны существовать поля {1} в реале существуют такие {2}'.format(table, ffields, efields))
        
    def check_database_version_1(self):
        self.check_tables_existance([u'deals', u'positions', u'deal_groups', u'accounts'])
        
    def check_database_version_2(self):
        self.check_tables_existance([u'deals', u'positions', u'deal_groups', u'accounts', u'deal_attributes'])
            

    def set_selected_stocks(self, stocks):
        self.begin_without_changes()
        self.connection.execute("delete from selected_stocks")
        if stocks and len(stocks) > 0:
            self.connection.executemany("insert into selected_stocks(stock) values (?)", map(lambda a: (a,), stocks))
        self.end_without_changes()

    def set_selected_accounts(self, accounts):
        self.begin_without_changes()
        self.connection.execute("delete from selected_accounts")
        if accounts and len(accounts) > 0:
            self.connection.executemany("insert into selected_accounts(account_id) select id from accounts where name = ?", map(lambda a: (a,), accounts))
        self.end_without_changes()

    def pset_selected_stocks(self, stocks):
        self.begin_without_changes()
        self.connection.execute("delete from pselected_stocks")
        if not is_null_or_empty(stocks):
            self.connection.executemany("insert into pselected_stocks (stock) values (?)", map(lambda a: (a,), stocks))
        self.end_without_changes()

    def pset_selected_accounts(self, accounts):
        self.begin_without_changes()
        self.connection.execute("delete from pselected_accounts")
        if not is_null_or_empty(accounts):
            self.connection.executemany("insert into pselected_accounts (account_id) select id from accounts where name = ?", map(lambda a: (a, ), accounts))
        self.end_without_changes()

    def begin_without_changes(self):
        if self._total_changes == None:
            self._total_changes = self.connection.total_changes

    def end_without_changes(self):
        if self._total_changes != None:
            self.last_total_changes += self.connection.total_changes - self._total_changes
            self._total_changes = None

    def delete_deals_by_ids(self, dids):
        self.connection.executemany("delete from deals where id = ?", map(lambda did: (did, ), dids))
        
    def recalculate_position_attributes(self, account_id):
        self.begin_without_changes()
        self.delete_position_attributes(account_id)
        self.generate_position_attributes(account_id)
        self.end_without_changes()

    def delete_position_attributes(self, account_id):
        self.connection.execute("delete from internal_position_attributes where position_id in (select distinct p.id from positions p inner join deals d where d.account_id = ?)", (account_id, ))

        
    def generate_position_attributes(self, account_id):
        (my_money,) = self.connection.execute("select first_money from accounts where id = ? limit 1", (account_id, )).fetchone()
        net = my_money
        gross = my_money 
        comm = 0
        for (pid, ticket, open_datetime, close_datetime, open_coast, close_coast, count, open_volume, close_volume, broker_comm, stock_comm, pl_net, pl_gross) in self.connection.execute("select p.id, p.ticket, p.open_datetime, p.close_datetime, p.open_coast, p.close_coast, p.count, p.open_volume, p.close_volume, p.broker_comm, p.stock_comm, p.pl_net, p.pl_gross from positions p where exists(select d.* from deals d where d.position_id = p.id and d.account_id = ?) and not exists(select d.* from deals d where d.position_id = p.id and d.account_id <> ?) order by p.close_datetime, p.open_datetime", (account_id, account_id)):
            oldnet = net
            net += pl_net
            oldgross = gross
            gross += pl_gross
            oldcomm = comm
            comm += stock_comm + broker_comm
            self._insert_from_hash("internal_position_attributes", {"position_id" : pid,
                                                                    "net_before" : oldnet,
                                                                    "net_after" : net,
                                                                    "gross_before" : oldgross,
                                                                    "gross_after" : gross,
                                                                    "comm_before" : oldcomm,
                                                                    "comm_after" : comm,
                                                                    "plnet_acc" : (pl_net / oldnet * 100),
                                                                    "account_id" : account_id})
                                                                    
                                                                    
                                                                    

    def create_new(self, filename):
        self.open(filename)
        self.connection.execute("pragma user_version = {0}".format(self.current_user_version))
        self.connection.execute("""create table positions(
        id integer primary key not null,
        ticket text not null,
        direction integer not null,
        open_datetime datetime not null,
        close_datetime datetime not null,
        open_coast real not null,
        close_coast real not null,
        count integer not null,
        open_volume real not null,
        close_volume real not null,
        broker_comm real,
        broker_comm_nds real,
        stock_comm real,
        stock_comm_nds real,
        pl_gross real not null,
        pl_net real not null)""")
        self.connection.execute("create index positions_ticket on positions(ticket)")
        
        self.connection.execute("""
        create table accounts(
        id integer primary key not null,
        name text not null,
        first_money float not null,
        currency text,
        unique(name))""")

        self.connection.execute("create table deal_groups (id integer primary key not null, deal_sign integer not null, ticket text not null)")
        self.connection.executescript("""
        create index deal_groups_deal_sign on deal_groups(deal_sign);
        create index deal_groups_ticket on deal_groups(ticket);""")

        self.connection.execute("""create table deals(
        id integer primary key not null,
        sha1 text,
        parent_deal_id integer,
        not_actual integer,
        group_id integer,
        account_id integer,
        datetime datetime not null,
        datetime_day text,
        security_type text,
        security_name text not null,
        grn_code text,
        price real not null,
        quantity integer not null,
        volume real,
        deal_sign integer not null,
        broker_comm real,
        broker_comm_nds real,
        stock_comm real,
        stock_comm_nds real,
        position_id integer,
        foreign key (position_id) references positions(id) on delete set null,
        foreign key (parent_deal_id) references deals(id) on delete cascade,
        foreign key (group_id) references deal_groups(id) on delete set null,
        foreign key (account_id) references accounts(id) on delete set null,
        unique(sha1, account_id)
        )""")
        self.connection.executescript("""
        create index delas_not_actual on deals(not_actual);
        create index deals_datetime on deals(datetime);
        create index deals_security_name on deals(security_name);
        create index deals_quantity on deals(quantity);
        create index deals_deal_sign on deals(deal_sign);""")
        self.connection.execute("""
        create table deal_attributes(
        id integer primary key not null,
        deal_id integer not null,
        name text not null,
        value text,
        unique(deal_id, name),
        foreign key (deal_id) references deals(id) on delete cascade)""")
        self.connection.executescript("""
        create index deal_attributes_name on deal_attributes(name);""")

        self.create_temporary_tables()
        self.connection.commit()
        self.connection.execute("begin transaction")


    def delete_empty_positions(self):
        """deletes positions which has no one deal assigned to"""
        self.connection.execute("delete from positions where id in (select p.id from positions p where not exists(select d.id from deals d where d.position_id = p.id))")

    def delete_empty_deal_groups(self):
        self.connection.execute("delete from deal_groups where id in (select dg.id from deal_groups dg where not exists(select d.id from deals d where d.group_id = dg.id))")


    def delete_broken_positions(self, account_id):
        """deletes positions which has unbalanced set of deals assigned to"""
        self.connection.execute("delete from positions where id in (select id from (select p.id as id, sum(d.quantity) as count from positions p inner join deals d on d.position_id = p.id where d.account_id = ? group by p.id) where abs(count) > 0.00001)", (account_id, ))

    def join_deals_leaves(self, account_id):
        """looks for deals which has only deals assigned to and not to any position and delete it's child deals"""
        try_again = True
        while try_again:
            try_again = False
            for (did, ) in self.connection.execute("select d.id from deals d where exists(select dd.id from deals dd where dd.position_id is null and dd.parent_deal_id = d.id) and not exists(select dd.id from deals dd where dd.position_id is not null and dd.parent_deal_id = d.id) and d.account_id = ?", (account_id, )):
                self.connection.execute("delete from deals where parent_deal_id = ?", (did, ))
                self.connection.execute("update deals set not_actual = null where id = ?", (did, ))
                try_again = True

    def close(self):
        if self.connection:
            if self.last_total_changes < self.connection.total_changes and self.filename != ":memory:":
                raise Exception(u'В базе данных проведено {0} изменений. Выполните Commit или Rollback'.format(self.connection.total_changes - self.last_total_changes))
            else:
                self.connection.close()
                self.connection = None
                self.have_changes = False
                self.filename = None

    def get_from_list(self, coats):
        for coat in coats:
            if (coat.has_key('sha1') and coat['sha1'] != None) and ((not coat.has_key('account_id')) or coat['account_id'] == None):
                (c, ) = self.connection.execute("select count(*) from deals where sha1 = ? and account_id is null", (coat['sha1'],)).fetchone()
                if c >= 1:
                    continue
            try:
                coat['datetime_day'] = datetime.date.fromtimestamp(time.mktime(coat['datetime'].timetuple())).isoformat()
                incoat = copy(coat)
                attrs = gethash(incoat, "attributes")
                if attrs != None:
                    del incoat["attributes"]
                cid = self._insert_from_hash('deals', incoat).lastrowid
                if attrs != None and len(attrs) > 0:
                    self.connection.executemany("insert into deal_attributes(deal_id, name, value) values (?, ?, ?)",
                                                map(lambda a: tuple([cid] + list(a)), attrs))
                    
                
            except sqlite3.IntegrityError:
                continue
            except Exception as e:
                raise e

    def get_update_deal_from_hash(self, dhash):
        if not isinstance(gethash(dhash, "id"), int):
            raise Exception("id must be int")
        dh = copy(dhash)
        del dh["id"]
        attrs = gethash(dh, "attributes")
        if attrs != None:
            del dh["attributes"]
        self.connection.execute("delete from deal_attributes where deal_id = ?", (dhash["id"], ))
        self._update_from_hash("deals", dhash["id"], dh)
        if attrs != None and len(attrs) > 0:
            self.connection.executemany("insert into deal_attributes(deal_id, name, value) values (?, ?, ?)",
                                        map(lambda a: tuple([dhash["id"]] + list(a)), attrs))
        

    def get_from_list_in_account(self, account, coats):
        (count, ) = self.connection.execute("select count(*) from accounts where id = ?", (account,)).fetchone()
        if count != 1:
            raise Exception(u'Счета с id {0} не существует или есть более чем 1'.format(account))
        def one(a):
            ret = a
            ret["account_id"] = account
            return ret
        self.get_from_list(map(one, coats))
            
    def get_from_source_in_account(self, account, source):
        if account != None:
            self.get_from_list_in_account(account, source.get_deals_list())
        else:
            self.get_from_list(source.get_deals_list())

    def get_from_source(self, source):
        self.get_from_list(source.get_deals_list())
        
    def commit(self):
        self.connection.commit()
        self.last_total_changes = self.connection.total_changes
        self.connection.execute("begin transaction")

    def rollback(self):
        self.connection.rollback()
        self.last_total_changes = self.connection.total_changes
        self.connection.execute("begin transaction")

    def _insert_into(self, tablename, fields, values):
        ret = self.connection.execute(u'insert into {0}({1}) values ({2})'.format(tablename, reduce(lambda a, b: u'{0}, {1}'.format(a, b), fields), reduce(lambda a, b: u'{0}, {1}'.format(a, b), map(lambda a: '?', fields))), values)
        return ret

    def _insert_from_hash(self, tablename, hashtable):
        fields, values = [], []
        for key in hashtable:
            fields.append(key)
            values.append(hashtable[key])
        return self._insert_into(tablename, fields, values)

    def _update_from_hash(self, tablename, recid, hashtable):
        keys = hashtable.keys()
        vals = map(lambda key: hashtable[key], keys)
        setfields = reduce(lambda a, b:u'{0}, {1}'.format(a, b), map(lambda key:u'{0} = ?'.format(key), keys))
        q = u'update {table} set {sets} where id = ?'.format(table = tablename, sets = setfields)
        self.connection.execute(q, vals + [recid])

    def check_balance(self):
        for (account,) in self.connection.execute("select distinct id from accounts"):
            for (ticket,) in self.connection.execute("select distinct security_name from deals"):
                (buy, ) = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ? and account_id = ?", (-1, ticket, account)).fetchone()
                (sell, ) = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ? and account_id = ?", (1, ticket, account)).fetchone()
                if buy != sell:
                    raise Exception(u'В отчете несбалансированноый набор сделок по бумаге {0}. Куплено - продано = {1}'.format(ticket, buy - sell))

    def make_position(self, first_id, second_id):
        #print((first_id, second_id))
        def roll_id_or(idarray):
            if 1 == len(idarray):
                return u'(id = {0})'.format(idarray[0])
            else:
                return u'({0})'.format(reduce(lambda a, b: u'{0} or {1}'.format(a, b), map(lambda a: u'id = {0}'.format(a), idarray)))
        if not isinstance(first_id, list):
            first_id = [first_id]
        if not isinstance(second_id, list):
            second_id = [second_id]
        (oticks,) = self.connection.execute("select count(*) from (select distinct security_name from deals where {0})".format(roll_id_or(first_id))).fetchone()
        (cticks,) = self.connection.execute("select count(*) from (select distinct security_name from deals where {0})".format(roll_id_or(second_id))).fetchone()
        (accs, ) = self.connection.execute("select count(*) from (select distinct account_id from deals where {0})".format(roll_id_or(first_id + second_id))).fetchone() or (None, )
        if accs == None:
            raise Exception(u'Сделки не привязаны ни к одному счету')
        elif accs > 1:
            raise Exception(u'Сделки привяаны более чем к одному счету')
        if 1 != oticks:
            raise Exception(u'Чето косяк: сделки на открытие позиции идут по {0} разным тикерам'.format(oticks))
        if 1 != cticks:
            raise Exception(u'Чето косяк: сделки на закрытие позиции идут по {0} разным тикерам'.format(cticks))
        (otick,) = self.connection.execute("select security_name from deals where id = ?", (first_id[0],)).fetchone()
        (ctick,) = self.connection.execute("select security_name from deals where id = ?", (second_id[0],)).fetchone()
        if otick != ctick:
            raise Exception(u'КЭП предупреждает: нельзя открыть позицию по бумаге {0} и закрыть по {1}'.format(otick, ctick))
        (oquant, osign_sum) = self.connection.execute("select sum(quantity), sum(deal_sign * quantity) from deals where {0}".format(roll_id_or(first_id))).fetchone()
        (cquant, csign_sum) = self.connection.execute("select sum(quantity), sum(deal_sign * quantity) from deals where {0}".format(roll_id_or(second_id))).fetchone()
        if oquant != abs(osign_sum):
            raise Exception(u'Чето косяк: в открывающих сделках есть сделки в разную сторону либо {0} либо {1} сделок не в ту сторону'.format(abs(oquant - abs(osign_sum)), abs(osign_sum)))
        if cquant != abs(csign_sum):
            raise Exception(u'Чето косяк: в закрывающих сделках есть сделки в разную сторону либо {0} либо {1} сделок не в ту сторону'.format(abs(cquant - abs(csign_sum)), abs(csign_sum)))
        
        if abs(osign_sum)/osign_sum != -abs(csign_sum)/csign_sum:
            raise Exception(u'Попытка создать закрыть позицию сделками в ту же сторону')
        
        oprice = None
        cprice = None
        if first_id.__len__() > 1:
            (a,b) = self.connection.execute("select sum(volume), sum(quantity) from deals where {0}".format(roll_id_or(first_id))).fetchone()
            oprice = a / b
        else:
            (oprice,) = self.connection.execute("select price from deals where id = ?", (first_id[0],)).fetchone()

        if second_id.__len__() > 1:
            (a,b) = self.connection.execute("select sum(volume), sum(quantity) from deals where {0}".format(roll_id_or(second_id))).fetchone()
            cprice = a / b
        else:
            (cprice,) = self.connection.execute("select price from deals where id = ?", (second_id[0],)).fetchone()
        
        (ovolume, odatetime, obroker_comm, obroker_comm_nds, ostock_comm, ostock_comm_nds) = self.connection.execute("select sum(volume), avg(datetime), sum(broker_comm), sum(broker_comm_nds), sum(stock_comm), sum(stock_comm_nds) from deals where {0}".format(roll_id_or(first_id))).fetchone()
        (cvolume, cdatetime, cbroker_comm, cbroker_comm_nds, cstock_comm, cstock_comm_nds) = self.connection.execute("select sum(volume), avg(datetime), sum(broker_comm), sum(broker_comm_nds), sum(stock_comm), sum(stock_comm_nds) from deals where {0}".format(roll_id_or(second_id))).fetchone()
        dsign = abs(osign_sum) / osign_sum
        pos_id = self._insert_into("positions",
                                   ["ticket", "direction", "count",
                                    "open_volume", "close_volume", "open_coast", "close_coast",
                                    "open_datetime", "close_datetime", "broker_comm", "broker_comm_nds",
                                    "stock_comm", "stock_comm_nds", "pl_gross", "pl_net"],
                                   (otick, dsign, oquant, ovolume, cvolume, oprice, cprice,
                                    odatetime, cdatetime, obroker_comm + cbroker_comm,
                                    obroker_comm_nds + cbroker_comm_nds, ostock_comm + cstock_comm,
                                    ostock_comm_nds + cstock_comm_nds, (ovolume - cvolume) * dsign,
                                    (ovolume - cvolume) * dsign - (obroker_comm + cbroker_comm + ostock_comm + cstock_comm))).lastrowid
        self.connection.execute("update deals set position_id = ? where {0}".format(roll_id_or(first_id + second_id)), (pos_id,))
        

    def make_position_from_groups(self, opos, cpos):
        self.make_position(map(lambda a:a[0], self.connection.execute("select d.id from deals d where d.position_id is null and d.not_actual is null and d.group_id = ?", (opos,)).fetchall()), map(lambda a:a[0], self.connection.execute("select d.id from deals d where d.position_id is null and d.not_actual is null and d.group_id = ?", (cpos,)).fetchall()))

    def make_groups(self, ticket):
        for (account,) in self.connection.execute("select id from accounts"):
            self.make_groups_in_account(account, ticket)

    def make_account(self, name, first_money, currency):
        """makes new account and returns it's id"""
        return self._insert_from_hash("accounts", {"name" : name,
                                                   "first_money" : first_money,
                                                   "currency" : currency}).lastrowid

    def delete_positions_by_ids(self, pids):
        self.connection.executemany("delete from positions where id = ?", map(lambda a: (a, ), pids))

    def make_groups_in_account(self, account, ticket):
        for sign in [-1, 1]:
            opened_signed = []
            for (deal_id, deal_datetime) in self.connection.execute("select id, datetime from deals where position_id is null and not_actual is null and group_id is null and security_name = ? and deal_sign = ? and account_id = ? order by datetime", (ticket, sign, account)):
                (group_id,) = self.connection.execute("select g.id from deals d inner join deal_groups g on d.group_id = g.id where g.ticket = ? and g.deal_sign = ? and d.position_id is null and d.account_id = ? and d.datetime <= ? and ? - d.datetime <= 5 order by d.datetime desc", (ticket, sign, account, deal_datetime, deal_datetime)).fetchone() or (None, )
                if group_id:
                    self.connection.execute("update deals set group_id = ? where id = ?", (group_id, deal_id))
                else:
                    new_group_id = self._insert_into("deal_groups", ["deal_sign", "ticket"], [sign, ticket]).lastrowid
                    self.connection.execute("update deals set group_id = ? where id = ?", (new_group_id, deal_id))

    def delete_groups_in_account(self, account, ticket):
        self.connection.execute("delete from deal_groups where id in (select distinct g.id from deals_groups g inner join deals d on d.group_id = g.id where d.accaaount_id = ? and d.security_name = ?)", (account, ticket))

    def delete_positions_in_account(self, account, ticket):
        self.connection.execute("delete from positions where id in (select p.id from positions p inner join deals d on d.position_id = p.id where d.account_id = ? and d.security_name = ?)", (account, ticket))
        
    def split_deal(self, deal_id, needed_quantity):
        (quant,) = self.connection.execute("select quantity from deals where id = ?", (deal_id,)).fetchone() or (None,)
        if not quant:
            raise Exception(u'There is no deal with id {0}'.format(deal_id))
        (pid,) = self.connection.execute("select not_actual from deals where id = ?", (deal_id,)).fetchone()
        if pid:
            raise Exception(u'сделка с номером {0} уже разбита'.format(deal_id))
        if quant == needed_quantity:
            return [deal_id]
        if quant < needed_quantity:
            raise Exception(u'КО в недоразумении: попытка разбить сделку из {0} позиций чтобы была сделка с {0} позициями'.format(quant, needed_quantity))
        m1 = [needed_quantity] + map(lambda a: float(needed_quantity) / quant, range(0, 5))
        m2 = [quant - needed_quantity] + map(lambda a: float(quant - needed_quantity) / quant, range(0, 5))
        ret = []
        for mm in [m1, m2]:
            cid = self.connection.execute("insert into deals (account_id, parent_deal_id, group_id, datetime, datetime_day, security_type, security_name, grn_code, price, quantity, volume, deal_sign, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds, position_id) select account_id, ?, group_id, datetime, datetime_day, security_type, security_name, grn_code, price, ?, volume * ?, deal_sign, broker_comm * ?, broker_comm_nds * ?, stock_comm * ?, stock_comm_nds * ?, position_id from deals where id = ?", [deal_id] + mm + [deal_id]).lastrowid
            ret.append(cid)
        self.connection.execute("update deals set not_actual = 1 where id = ?", (deal_id,))
        return ret

    def split_deal_group(self, group_id, needed_quantity):
        (quant,) = self.connection.execute("select sum(d.quantity) from deals d inner join deal_groups g on d.group_id = g.id where g.id = ? and d.not_actual is null", (group_id,)).fetchone() or (None, )
        if not quant:
            raise Exception(u'{0} это не существующий id группы'.format(group_id))

        if quant < needed_quantity:
            raise Exception(u'Попытка разбить группу из {0} контрактов на группу с {1} контрактами'.format(quant, needed_quantity))
        if quant == needed_quantity:
            return [group_id]

        def reduce_and_not_id(ids):
            if 1 == len(ids):
                return u'(id <> {0})'.format(ids[0])
            else:
                return u'({0})'.format(reduce(lambda a, b:u'{0} and {1}'.format(a,b), map(lambda a: u'id <> {0}'.format(a), ids)))
        
        splited = []                    # отобранные сделки
        summ = 0                        # сумма отобранных сделок
        for deal in self.connection.execute("select id, quantity from deals where group_id = ? and not_actual is null order by quantity desc", (group_id,)):
            if summ + deal[1] <= needed_quantity:
                splited.append(deal)
                summ += deal[1]
                if summ == needed_quantity:
                    break
                
        if summ < needed_quantity:      # не получилось отобрать ровное количество сделок будем разбивать сделку
            (spdid,) = self.connection.execute("select id from deals where not_actual is null and group_id = ? and quantity > ? and {0} order by datetime".format(len(splited) > 0 and reduce_and_not_id(map(lambda a:a[0], splited)) or '1 = 1'), (group_id, needed_quantity - summ)).fetchone() or (None,)
            if not spdid:
                raise Exception(u'Произошла странная ошибка: в группе не оказалось сделки которая там должна быть')
            spp = self.split_deal(spdid, needed_quantity - summ)[0] # id сделки с нужным количеством контрактов
            splited.append(self.connection.execute("select id, quantity from deals where id = ?",(spp,)).fetchone())

        new_group_id = self.connection.execute("insert into deal_groups(deal_sign, ticket) select deal_sign, ticket from deal_groups where id = ?",(group_id,)).lastrowid # создаем другую группу
        self.connection.execute("update deals set group_id = ? where {0} and not_actual is null and group_id = ?".format(reduce_and_not_id(map(lambda a:a[0], splited))), (new_group_id, group_id)) # приписываем новой группе все сделки из нашей группы которые актуальные и не входят в множество отобранных
        return [group_id, new_group_id]
            
            
    def make_positions(self):
        for (account, ) in self.connection.execute("select id from accounts"):
            self.make_positions_in_account(account)

    def make_positions_in_account(self, account):
        
        def fetch_one_pair_and_close(self, ticket):
            (ogid, osign, oquant, odate) = self.connection.execute("select * from (select g.id as id, g.deal_sign as sign, sum(d.quantity) as quantity, max(d.datetime) as datetime from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and d.position_id is null and d.account_id = ? and g.ticket = ? group by g.id) where quantity > 0 order by datetime", (account, ticket)).fetchone() or (None, None, None, None)
            if ogid:
                (cgid, cquant) = self.connection.execute("select id, quantity from (select g.id as id, sum(d.quantity) as quantity, min(d.datetime) as datetime from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and d.position_id is null and d.account_id = ? and g.ticket = ? and g.deal_sign = ? group by g.id) where quantity > 0 and datetime >= ? order by datetime", (account, ticket, -osign, odate)).fetchone() or (None, None)
                if cgid:
                    if oquant < cquant:
                        cgid = self.split_deal_group(cgid, oquant)[0]
                    elif oquant > cquant:
                        ogid = self.split_deal_group(ogid, cquant)[0]
                    self.make_position_from_groups(ogid, cgid)
                    return True
            return False
            
        for (ticket,) in self.connection.execute("select distinct security_name from deals where position_id is null and not_actual is null"):
            self.make_groups_in_account(account, ticket)
            
        for (ticket,) in self.connection.execute("select distinct security_name from deals"):
            while fetch_one_pair_and_close(self, ticket):
                pass
            
            
                
        # (pc,) = self.connection.execute("select count(*) from deals where position_id is null and not_actual is null").fetchone()
        # if 0 != pc:
        #     raise Exception(u'Не получилось расписать по позициям {0} сделок'.format(pc))
        
        self.ready = True

if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
