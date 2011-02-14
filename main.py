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
        self.window.connect("destroy", gtk.main_quit)
        self.choose_file.connect("file-set", self.file_set)
        self.segfault.connect("clicked", self.clicked, self._gen_seg)
        self.axce1.connect("clicked", self.clicked, self._gen_axcel)

    def _gen_seg(self):
        ret = u''
        for pos in self.deals.connection.execute("select ticket, direction, open_coast, close_coast, count, broker_comm + stock_comm, pl_gross, pl_net, open_datetime, close_datetime from positions order by close_datetime, open_datetime"):
            (open_datetime, close_datetime) = pos[-2:]
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), pos[:-2])
            ret += u'\t{0}\t{1}\n'.format(mx.DateTime.DateTimeFromTicks(open_datetime).Format(), mx.DateTime.DateTimeFromTicks(close_datetime).Format())
        if self.comma.props.active:
            ret = ret.replace(".", ",")
        return ret

    def _gen_axcel(self):
        ret = u''
        for deal in self.deals.connection.execute("select security_name, datetime, quantity, price, volume, deal_sign, broker_comm + stock_comm from deals order by security_name, datetime"):
            ret += u'{0}\t{1}\t{2}\t'.format(deal[0], deal[1], mx.DateTime.DateTimeFromTicks(deal[1]).Format())
            a = u'{0}\n'.format(reduce(lambda a, b: u'{0}\t{1}'.format(a,b), deal[2:]))
            if self.comma.props.active:
                a = a.replace(".", ",")
            ret += a
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
        if not (self.common_deal.length > 0 and self.account_totally.length > 1 and self.briefcase.length > 1):
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
        (ticket, quantity, osign, oprice, ovolume, odatetime, obroker_comm, obroker_comm_nds, ostock_comm, ostock_comm_nds) = self.connection.execute("select security_name, quantity, deal_sign, price, volume, datetime, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds from deals where id = ?", (first_id,)).fetchone()
        (csign, cprice, cvolume, cdatetime, cbroker_comm, cbroker_comm_nds, cstock_comm, cstock_comm_nds) = self.connection.execute("select deal_sign, price, volume, datetime, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds from deals where id = ?", (second_id,)).fetchone()
        if osign != -(csign):
            raise Exception(u'Попытка создать позицию из сделок в одну сторону')
        
        pos_id = self._insert_into("positions",
                                   ["ticket", "direction", "count",
                                    "open_volume", "close_volume", "open_coast", "close_coast",
                                    "open_datetime", "close_datetime", "broker_comm", "broker_comm_nds",
                                    "stock_comm", "stock_comm_nds", "pl_gross", "pl_net"],
                                   (ticket, osign, quantity, ovolume, cvolume, oprice, cprice,
                                    odatetime, cdatetime, obroker_comm + cbroker_comm,
                                    obroker_comm_nds + cbroker_comm_nds, ostock_comm + cstock_comm,
                                    ostock_comm_nds + cstock_comm_nds, (ovolume - cvolume) * osign,
                                    (ovolume - cvolume) * osign - (obroker_comm + cbroker_comm + ostock_comm + cstock_comm))).lastrowid
        self.connection.execute("update deals set position_id = ? where id = ? or id = ?", (pos_id, first_id, second_id))
        

        
        
            
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
                    
                
            
                        
                
        (pc,) = self.connection.execute("select count(*) from deals where position_id is null").fetchone()
        if 0 != pc:
            raise Exception(u'Не получилось расписать по позициям {0} сделок'.format(pc))
        
        self.ready = True

if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
