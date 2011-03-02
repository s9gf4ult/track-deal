#!/bin/env python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import gtk
import sqlite3
import mx.DateTime
import re
import traceback

class main_ui():
    def __init__(self):
        a = gtk.Builder()
        a.add_from_file("main_ui.glade")
        self.window = a.get_object("main_window")
        self.axce1 = a.get_object("gen_axcel")
        self.segfault = a.get_object("gen_seg")
        self.choose_file = a.get_object("choose_file")
        self.buffer = a.get_object("buffer")
        self.comma = a.get_object("comma_separator")
        self.stock_buttons = a.get_object("stock_buttons")
        self.filefilter = a.get_object("filefilter")
        self.filefilter.add_mime_type("application/xml")
        self.window.connect("destroy", gtk.main_quit)
        self.choose_file.connect("file-set", self.file_set)
        self.segfault.connect("clicked", self.clicked, self._gen_seg)
        self.axce1.connect("clicked", self.clicked, self._gen_axcel)

    def _gen_seg(self, ticks):
        ret = u''
        for pos in self.deals.connection.execute("select ticket, direction, count, open_coast, close_coast, broker_comm + stock_comm, open_datetime, close_datetime from positions where id <> -1 order by close_datetime, open_datetime"):
            if not pos[0] in ticks:
                continue
            (open_datetime, close_datetime) = map(lambda a: mx.DateTime.DateTimeFromTicks(a).Format("%d.%m.%Y"), pos[-2:])
            ret += u'{0}\t{1}'.format(pos[0], -1 == pos[1] and 'L' or 'S')
            v = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), pos[2:-2])
            if self.comma.props.active:
                v = v.replace('.', ',')
            ret += u'\t{0}\t\t\t\t\t\t{1}\t{2}\n'.format(v, open_datetime, close_datetime)
        return ret

    def _gen_axcel(self, ticks):
        ret = u''
        for pos in self.deals.connection.execute("select open_datetime, close_datetime, ticket, direction, open_coast, close_coast, count, open_volume, close_volume from positions where id <> -1 order by close_datetime, open_datetime"):
            if not pos[2] in ticks:
                continue
            ddd = map(lambda a: mx.DateTime.DateTimeFromTicks(a), pos[:2])
            vvv = map(lambda a: [a.Format("%d.%m.%Y"), a.Format("%H:%M:%S")], ddd)
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), vvv[0] + vvv[1])
            ret += u'\t{0}\t{1}'.format(pos[2], -1 == pos[3] and 'L' or 'S')
            aa = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: float(a).__trunc__(), pos[4:]))
            if self.comma.props.active:
                aa = aa.replace('.', ',')
            ret += u'\t{0}\n'.format(aa)
            
        return ret

    def clicked(self, button, call_me):
        if hasattr(self, "coats") and self.coats.checked and hasattr(self, "deals") and self.deals.ready:
            bc = []
            self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.get_active() and bc.append(wid.get_label()))
            self.buffer.set_text(call_me(bc))
        else:
            self.show_error(u'Сначала надо указать валидный файл')

    def show_error(self, text):
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = self.window)
        dial.props.text = text
        dial.run()
        dial.destroy()

    def file_set(self, widget):
        try:
            self.coats = xml_parser(widget.get_filename())
        except:
            self.show_error(u'Это походу не xml')
            return

        try:
            self.coats.check_file()
            self.deals = deals_proc(self.coats)
            self.deals.check_balance()
            self.deals.make_positions()
        except Exception as e:
            self.show_error(traceback.format_exc())
            return

        self.stock_buttons.foreach(self.stock_buttons.remove)
        for (ticket,) in self.deals.connection.execute("select distinct security_name from deals order by security_name"):
            b = gtk.ToggleButton(label = ticket)
            b.set_active(True)
            self.stock_buttons.pack_start(b, False, True, 5)

        resall = gtk.Button(u'Сбросить все')
        resall.connect("clicked", lambda ww: self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(False)))
        self.stock_buttons.pack_end(resall, False, True)
        invall = gtk.Button(u'Реверс все')
        invall.connect("clicked", lambda ww: self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(not wid.get_active())))
        self.stock_buttons.pack_end(invall, False, True)
            
        self.window.show_all()
            
    def show(self):
        self.window.show_all()

class xml_parser():
    def __init__(self, filename):
        self.xml = parse(filename)
        self.checked = False

    def check_file(self):
        if not (self.xml.childNodes.length == 1 and self.xml.childNodes[0].nodeName == "report"):
            raise Exception(u'Нет тега report')
        self.report = self.xml.childNodes[0]
        for name in ["common_deal", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise Exception("there is no {0} in report or more that one found".format(name))
        self.common_deal = self.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
        self.account_totally = self.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
        #self.briefcase = self.report.getElementsByTagName("briefcase_position")[0].getElementsByTagName("item")
        if not (self.common_deal.__len__() > 0 and self.account_totally.__len__() > 1):
            raise Exception(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        self.checked=True
        
class deals_proc():
    def __init__(self, coats):
        self.ready = False
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("pragma foreign_keys=on")
        sqlite3.register_adapter(str, lambda a: a.decode(u'utf-8'))
        self.connection.execute("""create table positions(
        id integer primary key not null,
        ticket text not null,
        direction integer not null,
        open_datetime real not null,
        close_datetime real not null,
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
        

        self.connection.execute("create table deal_groups (id integer primary key not null, deal_sign integer not null, ticket text not null)")
        self.connection.executescript("""
        create index deal_groups_deal_sign on deal_groups(deal_sign);
        create index deal_groups_ticket on deal_groups(ticket);""")

        self.connection.execute("""create table deals(
        id integer primary key not null,
        parent_deal_id integer,
        not_actual integer,
        group_id integer,
        datetime real not null,
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
        foreign key (position_id) references positions(id) on delete set null
        foreign key (parent_deal_id) references deals(id) on delete set null
        foreign key (group_id) references deal_groups(id) on delete set null)""")
        self.connection.executescript("""
        create index delas_not_actual on deals(not_actual);
        create index deals_datetime on deals(datetime);
        create index deals_security_name on deals(security_name);
        create index deals_quantity on deals(quantity);
        create index deals_deal_sign on deals(deal_sign);""")
        
        for coat in coats.common_deal:
            date = mx.DateTime.DateTime(*map(int, re.split("[-T:]+", coat.attributes.has_key('deal_time') and coat.attributes['deal_time'].value or (coat.attributes.has_key('deal_date') and coat.attributes['deal_date'].value))))
            x = [date.ticks(), date.Format("%Y%m%d")]
            x.extend(map(lambda name: coat.attributes.has_key(name) and coat.attributes[name].value, ('security_type', 'security_name', 'grn_code')))
            x.extend(map(lambda name: coat.attributes.has_key(name) and float(coat.attributes[name].value) or 0, ('price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds')))
            if x[7] == 0:
                x[7] = x[5] * x[6]
            self._insert_into("deals", ["datetime",
                                        "datetime_day",
                                        "security_type",
                                        "security_name",
                                        "grn_code",
                                        "price",
                                        "quantity",
                                        "volume",
                                        "deal_sign",
                                        "broker_comm",
                                        "broker_comm_nds",
                                        "stock_comm",
                                        "stock_comm_nds"], x)

    def _insert_into(self, tablename, fields, values):
        return self.connection.execute(u'insert into {0}({1}) values ({2})'.format(tablename, reduce(lambda a, b: u'{0}, {1}'.format(a, b), fields), reduce(lambda a, b: u'{0}, {1}'.format(a, b), map(lambda a: '?', fields))), values)

    def check_balance(self):
        for (ticket,) in self.connection.execute("select distinct security_name from deals"):
            buy = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ?", (-1, ticket)).fetchall()[0][0] or 0
            sell = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ?", (1, ticket)).fetchall()[0][0] or 0
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
        self.make_position(map(lambda a:a[0], self.connection.execute("select d.id from deals d where d.position_id is null and d.group_id = ?", (opos,)).fetchall()), map(lambda a:a[0], self.connection.execute("select d.id from deals d where d.position_id is null and d.group_id = ?", (cpos,)).fetchall()))

    def make_groups(self, ticket):
        for sign in [-1, 1]:
            opened_signed = []
            for (deal_id, deal_datetime) in self.connection.execute("select id, datetime from deals where position_id is null and not_actual is null and  security_name = ? and deal_sign = ? order by datetime", (ticket, sign)):
                (group_id,) = self.connection.execute("select id from (select max(d.datetime) as datetime, g.id as id from deals d inner join deal_groups g on d.group_id = g.id where g.ticket = ? and g.deal_sign = ? and d.position_id is null group by g.id) where datetime <= ? and ? - datetime <= 5 order by datetime desc", (ticket, sign, deal_datetime, deal_datetime)).fetchone() or (None, )
                if group_id:
                    self.connection.execute("update deals set group_id = ? where id = ?", (group_id, deal_id))
                else:
                    new_group_id = self._insert_into("deal_groups", ["deal_sign", "ticket"], [sign, ticket]).lastrowid
                    self.connection.execute("update deals set group_id = ? where id = ?", (new_group_id, deal_id))
        
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
            cid = self.connection.execute("insert into deals(parent_deal_id, group_id, datetime, datetime_day, security_type, security_name, grn_code, price, quantity, volume, deal_sign, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds, position_id) select ?, group_id, datetime, datetime_day, security_type, security_name, grn_code, price, ?, volume * ?, deal_sign, broker_comm * ?, broker_comm_nds * ?, stock_comm * ?, stock_comm_nds * ?, position_id from deals where id = ?", [deal_id] + mm + [deal_id]).lastrowid
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
        
        def fetch_one_pair_and_close(self, ticket):
            (ogid, osign, oquant, odate) = self.connection.execute("select * from (select g.id as id, g.deal_sign as sign, sum(d.quantity) as quantity, max(d.datetime) as datetime from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and d.position_id is null and g.ticket = ? group by g.id) where quantity > 0 order by datetime", (ticket,)).fetchone() or (None, None, None, None)
            if ogid:
                (cgid, cquant) = self.connection.execute("select id, quantity from (select g.id as id, sum(d.quantity) as quantity, min(d.datetime) as datetime from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and d.position_id is null and g.ticket = ? and g.deal_sign = ? group by g.id) where quantity > 0 and datetime >= ? order by datetime", (ticket, -osign, odate)).fetchone() or (None, None)
                if cgid:
                    if oquant < cquant:
                        cgid = self.split_deal_group(cgid, oquant)[0]
                    elif oquant > cquant:
                        ogid = self.split_deal_group(ogid, cquant)[0]
                    self.make_position_from_groups(ogid, cgid)
                    return True
            return False
            
        for (ticket,) in self.connection.execute("select distinct security_name from deals where position_id is null and not_actual is null"):
            self.make_groups(ticket)
            
        for (ticket,) in self.connection.execute("select distinct security_name from deals"):
            while fetch_one_pair_and_close(self, ticket):
                pass
            
            
                
        (pc,) = self.connection.execute("select count(*) from deals where position_id is null").fetchone()
        if 0 != pc:
            raise Exception(u'Не получилось расписать по позициям {0} сделок'.format(pc))
        
        self.ready = True

if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
