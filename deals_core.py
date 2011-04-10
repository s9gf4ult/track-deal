#!/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import time
import datetime
import re

class deals_proc():
    def __init__(self):
        sqlite3.register_adapter(str, lambda a: a.decode(u'utf-8'))
        sqlite3.register_adapter(datetime.datetime, lambda a: time.mktime(a.timetuple()))
        sqlite3.register_converter('datetime', lambda a: datetime.datetime.fromtimestamp(float(a)))
        self.connection = None
        self.have_changes = False

    def create_temporary_tables(self):
        self.connection.execute("create temporary table selected_stocks (id integer primary key not null, stock text, unique(stock))")


    def open(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename, detect_types = sqlite3.PARSE_DECLTYPES)
        self.create_temporary_tables()
        self.last_total_changes = self.connection.total_changes
        self.connection.execute("pragma foreign_keys=on")
        self.connection.execute("begin transaction")

    def open_existing(self, filename):
        self.open(filename)
        if 3 != self.connection.execute("select count(*) from sqlite_master where type = 'table' and (name = 'positions' or name = 'deals' or name = 'deal_groups')").fetchone()[0]:
            raise Exception(u'Эта sqlite3 база скорее всего не является базой созданной open-deals')

    def set_selected_stocks(self, stocks):
        ll = self.connection.total_changes
        self.connection.execute("delete from selected_stocks")
        if stocks and len(stocks) > 0:
            self.connection.executemany("insert into selected_stocks(stock) values (?)", map(lambda a: (a,), stocks))
        self.last_total_changes += self.connection.total_changes - ll
            

    def create_new(self, filename):
        self.open(filename)
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



        self.connection.commit()
        self.connection.execute("begin transaction")


    def delete_empty_positions(self):
        """deletes positions which has no one deal assigned to"""
        self.connection.execute("delete from positions where id in (select p.id from positions p where not exists(select d.id from deals d where d.position_id = p.id))")


    def delete_broken_positions(self):
        """deletes positions which has unbalanced set of deals assigned to"""
        self.connection.execute("delete from positions where id in (select id from (select p.id as id, sum(d.quantity) as count from positions p inner join deals d on d.position_id = p.id group by p.id) where abs(count) > 0.00001)")

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
                self._insert_from_hash('deals', coat)
            except sqlite3.IntegrityError:
                continue
            except Exception as e:
                raise e

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
        self.get_from_list_in_account(account, source.get_deals_list())

    def get_from_source(self, source):
        self.get_from_list(source.get_deals_list())
        
    def commit(self):
        self.connection.commit()
        self.last_total_changes = self.connection.total_changes

    def rollback(self):
        self.connection.rollback()
        self.last_total_changes = self.connection.total_changes

    def _insert_into(self, tablename, fields, values):
        ret = self.connection.execute(u'insert into {0}({1}) values ({2})'.format(tablename, reduce(lambda a, b: u'{0}, {1}'.format(a, b), fields), reduce(lambda a, b: u'{0}, {1}'.format(a, b), map(lambda a: '?', fields))), values)
        return ret

    def _insert_from_hash(self, tablename, hashtable):
        fields, values = [], []
        for key in hashtable:
            fields.append(key)
            values.append(hashtable[key])
        return self._insert_into(tablename, fields, values)

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
