#!/bin/env python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import gtk
import sqlite3
import mx.DateTime
import re

class main_ui():
    def __init__(self):
        a = gtk.Builder()
        a.add_from_file("main_ui.glade")
        self.window = a.get_object("main_window")
        self.axce1 = a.get_object("gen_axcel")
        self.segfault = a.get_object("gen_seg")
        self.choose_file = a.get_object("choose_file")
        self.buffer = a.get_object("buffer")
        self.window.connect("destroy", gtk.main_quit)
        self.choose_file.connect("file-set", self.file_set)
        self.segfault.connect("clicked", self.clicked, self._gen_seg)
        self.axce1.connect("clicked", self.clicked, self._gen_axcel)

    def _gen_seg(self):
        ret = u''
        for pos in self.deals.connection.execute("select ticket, direction, open_coast, close_coast, pl_gross, pl_net from positions order by close_datetime, open_datetime"):
            ret += u'{0}\n'.format(reduce(lambda a, b: u'{0}\t{1}'.format(a, b), pos))
        
        return ret

    def _gen_axcel(self):
        return "axcel"

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
            self.show_error(e.__str__())
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
            x = [mx.DateTime.DateTime(*map(int, re.split("[-T:]+", coat.attributes['deal_time'].value))).ticks()]
            x.extend(map(lambda name: coat.attributes[name].value, ('security_type', 'security_name', 'grn_code')))
            x.extend(map(lambda name: float(coat.attributes[name].value), ('price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds')))
            self.connection.execute("""insert into deals(
            datetime,
            security_type,
            security_name,
            grn_code,
            price,
            quantity,
            volume,
            deal_sign,
            broker_comm,
            broker_comm_nds,
            stock_comm,
            stock_comm_nds)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",x)

    def check_balance(self):
        for (ticket,) in self.connection.execute("select distinct security_name from deals"):
            buy = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ?", (-1, ticket)).fetchall()[0][0] or 0
            sell = self.connection.execute("select sum(quantity) from deals where deal_sign = ? and security_name = ?", (1, ticket)).fetchall()[0][0] or 0
            if buy != sell:
                raise Exception(u'В отчете несбалансированноый набор сделок по бумаге {0}. Куплено - продано = {1}'.format(ticket, buy - sell))
            
    def make_positions(self):
        for (ticket,) in self.connection.execute("select distinct security_name from deals where position_id is null"):
            # сгурппируем парные сделки с одинаковым количеством бумажек на покупку - продажу
            for (count,) in self.connection.execute("select distinct quantity from deals where position_id is null and security_name = ?", (ticket,)):
                for (open_sign, close_sign) in [(-1, 1), (1, -1)]:
                    for (open_id, open_datetime, open_price, open_volume, open_broker_comm, open_broker_comm_nds, open_stock_comm, open_stock_comm_nds) in self.connection.execute("select id, datetime, price ,volume, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds from deals where position_id is null and security_name = ? and quantity = ? and deal_sign = ? order by datetime", (ticket, count, open_sign)):
                        if 0 == self.connection.execute("select count(*) from deals where position_id is null and security_name = ? and quantity = ? and deal_sign = ? and datetime > ?", (ticket, count, close_sign, open_datetime)).fetchone()[0]:
                            break
                        (close_id, close_datetime, close_price, close_volume, close_broker_comm, close_broker_comm_nds, close_stock_comm, close_stock_comm_nds) = self.connection.execute("select id, datetime, price, volume, broker_comm, broker_comm_nds, stock_comm, stock_comm_nds from deals where position_id is null and security_name = ? and quantity = ? and deal_sign = ? and datetime > ? order by datetime",(ticket, count, close_sign, open_datetime)).fetchone()
                        pos_id = self.connection.execute("""insert into positions (
                        ticket, direction, open_datetime, close_datetime,
                        open_coast, close_coast,
                        count,
                        open_volume, close_volume,
                        broker_comm, broker_comm_nds,
                        stock_comm, stock_comm_nds,
                        pl_gross, pl_net) values (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                                         (ticket, open_sign, open_datetime, close_datetime,
                                                          open_price, close_price,
                                                          count,
                                                          open_volume, close_volume,
                                                          open_broker_comm + close_broker_comm, open_broker_comm_nds + close_broker_comm_nds,
                                                          open_stock_comm + close_stock_comm, open_stock_comm_nds + close_stock_comm_nds,
                                                          (open_volume - close_volume) * open_sign,
                                                          ((open_volume - close_volume) * open_sign) - (open_broker_comm + close_broker_comm + open_stock_comm + close_stock_comm))).lastrowid
                        self.connection.execute("update deals set position_id = ? where id = ? or id = ?", (pos_id, open_id, close_id))
                        
                        
                    
                
                

        
        self.ready = True

if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
