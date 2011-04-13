#!/bin/env python
# -*- coding: utf-8 -*-
from datetime_control import *
from combo_control import *
from number_range_control import number_control
from time_control import *
from select_control import *
from combo_select_control import *
from common_methods import *
import sys

class deal_adder_control:
    def __init__(self, builder):
        self.builder = builder
        def shorter(name):
            return self.builder.get_object("deal_adder_{0}".format(name))
        w = self.builder.get_object("deal_adder")
        w.add_buttons(gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.datetime = datetime_control(shorter("calendar"),
                                         time_control(shorter("hour"),
                                                      shorter("min"),
                                                      shorter("sec")))
        self.account = combo_select_control(shorter("account"))
        self.instrument = combo_control(shorter("stock"))
        self.market = combo_control(shorter("market"))
        self.price = number_control(shorter("price"), step_incr = 0.1, digits = 4)
        self.price.set_lower_limit(0)
        self.price.set_upper_limit(sys.float_info.max)
        self.count = number_control(shorter("count"))
        self.count.set_lower_limit(0)
        self.count.set_upper_limit(sys.maxint)
        self.direction = select_control({ -1 : shorter("buy_rb"),
                                          1 : shorter("sell_rb")})
        self.broker_comm = number_control(shorter("broker_comm"), step_incr = 0.1, digits = 4)
        self.broker_comm.set_lower_limit(0)
        self.broker_comm.set_upper_limit(sys.float_info.max)
        self.stock_comm = number_control(shorter("stock_comm"), step_incr = 0.1, digits = 4)
        self.stock_comm.set_lower_limit(0)
        self.stock_comm.set_upper_limit(sys.float_info.max)

    def run(self):
        w = self.builder.get_object("deal_adder")
        w.show_all()
        ret = w.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if not self.check_correctness():
                ret = w.run()
            else:
                w.hide()
                return self.get_deal_hash()
        w.hide()
        return None

    def get_deal_hash(self):
        return {"datetime" : self.datetime.get_datetime(),
                "security_name" : self.instrument.get_value(),
                "security_type" : self.market.get_value(),
                "price" : self.price.get_value(),
                "quantity" : self.count.get_value(),
                "deal_sign" : self.direction.get_value(),
                "broker_comm" : self.broker_comm.get_value(),
                "stock_comm" : self.stock_comm.get_value(),
                "broker_comm_nds" : 0,
                "stock_comm_nds" : 0,
                "account_id" : self.account.get_value(),
                "volume" : self.count.get_value() * self.price.get_value()}

    def load_from_hash(self, data):
        for (setter, key) in [(self.datetime.set_datetime, "datetime"),
                              (self.direction.set_value, "deal_sign"),
                              (self.account.set_value, "account_id"),
                              (self.instrument.set_value, "security_name"),
                              (self.market.set_value, "security_type"),
                              (self.price.set_value, "price"),
                              (self.count.set_value, "quantity"),
                              (self.broker_comm.set_value, "broker_comm")
                              (self.stock_comm.set_value, "stock_comm")]:
            m = gethash(data, key)
            if m != None:
                setter(m)
        

    def check_correctness(self):
        def notempty(str):
            return str and len(str) > 0
        def show_message(message):
            w = gtk.MessageDialog(parent = self.builder.get_object("deal_adder"), flags = gtk.DIALOG_MODAL, type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_OK, message_format = message)
            w.run()
            w.hide()
            w.destroy()
        mss = []
        if not notempty(self.instrument.get_value()):
            mss.append(u'Вы должны указать инструмент')
        if self.price.get_value() <= 0:
            mss.append(u'Вы должны указать цену контракта')
        if self.count.get_value() <= 0:
            mss.append(u'вы должны указать количество котрактов')
        if len(mss) > 0:
            show_message(reduce(lambda a, b: u'{0}\n{1}'.format(a, b), mss))
            return False
        else:
            return True

    def update_widget(self, security_names, security_types, accounts = None):
        self.instrument.update_widget(security_names)
        self.market.update_widget(security_types)
        self.account.update_widget(accounts, none_answer = -1)

    def set_current_datetime(self):
        self.datetime.set_current_datetime()

    def load_to_widget(self, data):
        for (callset, key) in [(self.datetime.set_datetime, "datetime"),
                               (self.instrument.set_value, "security_name"),
                               (self.market.set_value, "security_type"),
                               (self.price.set_value, "price"),
                               (self.count.set_value, "quantity"),
                               (self.direction.set_value, "deal_sign"),
                               (self.broker_comm.set_value, "broker_comm"),
                               (self.stock_comm.set_value, "stock_comm")]:
            if data.has_key(key):
                callset(data[key])
            
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = deal_adder_control(b)
    con.instrument.update_widget(["aaa", "bbbb", "ccc"])
    con.market.update_widget(["mark1", "mark10", "supermark"])
    con.load_to_widget({"datetime" : datetime.datetime(2010, 10, 10, 20, 10, 15),
                        "quantity" : 100})
    print(con.run())
