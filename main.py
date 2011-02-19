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
        self.filefilter = a.get_object("filefilter")
        self.filefilter.add_mime_type("application/xml")
        self.window.connect("destroy", gtk.main_quit)
        self.choose_file.connect("file-set", self.file_set)
        self.segfault.connect("clicked", self.clicked, self._gen_seg)
        self.axce1.connect("clicked", self.clicked, self._gen_axcel)

    def _gen_seg(self):
        ret = u''
        for pos in self.deals.connection.execute("select ticket, direction, count, open_coast, close_coast, broker_comm + stock_comm, open_datetime, close_datetime from positions order by close_datetime, open_datetime"):
            (open_datetime, close_datetime) = map(lambda a: mx.DateTime.DateTimeFromTicks(a).Format("%d.%m.%Y"), pos[-2:])
            ret += u'{0}\t{1}'.format(pos[0], -1 == pos[1] and 'L' or 'S')
            v = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), pos[2:-2])
            if self.comma.props.active:
                v = v.replace('.', ',')
            ret += u'\t{0}\t\t\t\t\t\t{1}\t{2}\n'.format(v, open_datetime, close_datetime)
        return ret

    def _gen_axcel(self):
        ret = u''
        for pos in self.deals.connection.execute("select open_datetime, close_datetime, ticket, direction, open_coast, close_coast, count, open_volume, close_volume from positions order by close_datetime, open_datetime"):
            ddd = map(lambda a: mx.DateTime.DateTimeFromTicks(a), pos[:2])
            vvv = map(lambda a: [a.Format("%d.%m.%Y"), a.Format("%H:%M:%S")], ddd)
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), vvv[0] + vvv[1])
            ret += u'\t{0}\t{1}'.format(pos[2], -1 == pos[3] and 'L' or 'S')
            aa = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), pos[4:])
            if self.comma.props.active:
                aa = aa.replace('.', ',')
            ret += u'\t{0}\n'.format(aa)
            
        return ret

    def clicked(self, button, call_me):
        if hasattr(self, "coats") and self.coats.checked and hasattr(self, "deals") and self.deals.ready:
            self.buffer.set_text(call_me())
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
        for name in ["common_deal", "briefcase_position", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise Exception("there is no {0} in report or more that one found".format(name))
        self.common_deal = self.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
        self.account_totally = self.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
        self.briefcase = self.report.getElementsByTagName("briefcase_position")[0].getElementsByTagName("item")
        if not (self.common_deal.__len__() > 0 and self.account_totally.__len__() > 1 and self.briefcase.__len__() > 0):
            raise Exception(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        self.checked=True
        
class deals_proc():
    def __init__(self, coats):
        self.ready = False
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("pragma foreign_keys=on")
        self.connection.execute("""create table positions(
        id integer primary key not null,
        ticket,
        direction integer,
        open_datetime real,
        close_datetime real,
        open_coast real,
        close_coast real,
        count integer,
        open_volume real,
        close_volume real,
        broker_comm real,
        broker_comm_nds real,
        stock_comm real,
        stock_comm_nds real,
        pl_gross real,
        pl_net real)""")

        self.connection.execute("""create table deals(
        id integer primary key not null,
        datetime real,
        datetime_day text,
        security_type text,
        security_name text,
        grn_code text,
        price real,
        quantity integer,
        volume real,
        deal_sign integer,
        broker_comm real,
        broker_comm_nds real,
        stock_comm real,
        stock_comm_nds real,
        position_id integer,
        foreign key (position_id) references positions(id) on delete set null)""")
        for coat in coats.common_deal:
            date = mx.DateTime.DateTime(*map(int, re.split("[-T:]+", coat.attributes['deal_time'].value)))
            x = [date.ticks(), date.Format("%Y%m%d")]
            x.extend(map(lambda name: coat.attributes[name].value, ('security_type', 'security_name', 'grn_code')))
            x.extend(map(lambda name: float(coat.attributes[name].value), ('price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds')))
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

    def make_position(self, first_id, second_id): # FIXME это надо сделать так чтобы можно было закрывать не сбалансированные позиции
        def roll_id_or(idarray):
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
        

    def try_make_grouped(self, deals):
        counting = map(lambda m: map(lambda a: [(isinstance(a, list) and (reduce(lambda x, y: x + y, map(lambda aa: aa[2], a)) * a[0][1]) or a[2] * a[1]), a], m), deals)
        print(counting)
        
            
    def make_positions(self):
        for (ticket,) in self.connection.execute("select distinct security_name from deals where position_id is null"):
            # проходим по сделкам запоминая сделки которые уже были и закрывая их если находим подходящую парную сделку
            
            opened_deals = []
            for deal in self.connection.execute("select id, deal_sign, quantity from deals where position_id is null and security_name = ? order by datetime", (ticket,)):
                oposing_deals = filter(lambda a: a[1] == -(deal[1]) and a[2] == deal[2], opened_deals)
                if 0 != oposing_deals.__len__():
                    opened_deals = filter(lambda a: a != oposing_deals[0], opened_deals)
                    self.make_position(oposing_deals[0][0], deal[0])
                    continue
                else:
                    opened_deals.append(deal)
                    
            opened_deals = []
            for sign in [-1, 1]:
                opened_signed = []
                for deal in self.connection.execute("select id, deal_sign, quantity, datetime from deals where position_id is null and security_name = ? and deal_sign = ? order by datetime", (ticket, sign)):
                    islastlist = [] != opened_signed and isinstance(opened_signed[-1], list)
                    if [] != opened_signed and deal[3] - (islastlist and opened_signed[-1][-1] or opened_signed[-1])[3] <= 5:
                        if islastlist:
                            opened_signed[-1].append(deal)
                        else:
                            opened_signed[-1] = [opened_signed[-1], deal]
                    else:
                        opened_signed.append(deal)
                opened_deals.append(opened_signed)

            opened_deals = self.try_make_grouped(opened_deals)
            # (pc, ) = self.connection.execute("select count(*) from deals where position_id is null and security_name = ?", (ticket, )).fetchone()
            # if 0 != pc:
            #     self.try_group_ungrouped(opened_deals)
                
        (pc,) = self.connection.execute("select count(*) from deals where position_id is null").fetchone()
        if 0 != pc:
            raise Exception(u'Не получилось расписать по позициям {0} сделок'.format(pc))
        
        self.ready = True

if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
