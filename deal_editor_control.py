#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import *
import sys
from datetime_control import datetime_control
from time_control import time_control
from select_control import select_control
from combo_control import combo_control
from number_range_control import number_control
from combo_select_control import combo_select_control

class deal_editor_control:
    def __init__(self, builder):
        self.builder = builder
        def shorter(name):
            return self.builder.get_object(name)
        w = self.builder.get_object("deal_editor")
        w.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        
        ##########
        # hiders #
        ##########
        self.hiders = []
        for (hcb, box) in [("deal_editor_change_datetime", "deal_editor_datetime_box"),
                           ("deal_editor_change_direction", "deal_editor_direction_box"),
                           ("deal_editor_change_account", "deal_adder_account1"),
                           ("deal_editor_change_instrument", "deal_adder_stock1"),
                           ("deal_editor_cnahge_stock", "deal_adder_market1"),
                           ("deal_editor_change_price", "deal_adder_price1"),
                           ("deal_editor_change_count", "deal_adder_count1"),
                           ("deal_editor_change_broker_comm", "deal_adder_broker_comm1"),
                           ("deal_editor_change_stock_comm", "deal_adder_stock_comm1")]:
            cb = self.builder.get_object(hcb)
            bb = self.builder.get_object(box)
            self.hiders.append(hide_control(cb, [bb]))

        ####################
        # datetime control #
        ####################
        self.datetime = datetime_control(shorter("deal_adder_calendar1"),
                                         time_control(shorter("deal_adder_hour1"),
                                                      shorter("deal_adder_min1"),
                                                      shorter("deal_adder_sec1")),
                                         checkbutton = shorter("deal_editor_change_datetime"),
                                         year = shorter("deal_editor_year"),
                                         month = shorter("deal_editor_month"),
                                         day = shorter("deal_editor_day"))

        self.instrument = combo_control(shorter("deal_adder_stock1"),
                                        shorter("deal_editor_change_instrument"))

        self.market = combo_control(shorter("deal_adder_market1"),
                                    shorter("deal_editor_cnahge_stock"))

        self.price = number_control(shorter("deal_adder_price1"), shorter("deal_editor_change_price"), step_incr = 0.1, digits = 4)
        self.count = number_control(shorter("deal_adder_count1"), shorter("deal_editor_change_count"))
        self.broker_comm = number_control(shorter("deal_adder_broker_comm1"), shorter("deal_editor_change_broker_comm"), step_incr = 0.1, digits = 4)
        self.stock_comm = number_control(shorter("deal_adder_stock_comm1"), shorter("deal_editor_change_stock_comm"), step_incr = 0.1, digits = 4)
        for name in ["deal_adder_price1", "deal_adder_count1", "deal_adder_broker_comm1", "deal_adder_stock_comm1"]:
            m = shorter(name)
            m.get_adjustment().set_all(lower = 0, upper = sys.float_info.max)
        self.change_account = shorter("deal_editor_change_account")
        self.account = combo_select_control(shorter("deal_adder_account1"))
        self.direction = select_control({-1 : shorter("deal_adder_buy_rb1"),
                                         1 : shorter("deal_adder_sell_rb1")}, shorter("deal_editor_change_direction"))


    def update_accounts(self, accounts):
        """accounts must be the list of tupples like this (account_id, account_name)"""
        self.account.update_widget(answers = accounts, none_answer = -1)

    def update_instruments(self, instruments):
        """instruments is a list of strings"""
        self.instrument.update_widget(instruments)

    def update_markets(self, markets):
        self.market.update_widget(markets)

    def update_widget(self, data):
        for (setfunc, key) in [(self.datetime.set_datetime, "datetime"),
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
                setfunc(m)

    def get_updating_hash(self):
        ret = {}
        for (getter, key) in [(self.datetime.get_datetime, "datetime"),
                              (self.direction.get_value, "deal_sign"),
                              (self.instrument.get_value, "security_name"),
                              (self.market.get_value, "security_type"),
                              (self.price.get_value, "price"),
                              (self.count.get_value, "quantity"),
                              (self.broker_comm.get_value, "broker_comm"),
                              (self.stock_comm.get_value, "stock_comm")]:
            m = getter()
            if m != None:
                ret[key] = m
        if self.change_account.get_active():
            ret["account_id"] = self.account.get_value()
        return ret
        

    def run(self):
        win = self.builder.get_object("deal_editor")
        win.show_all()
        ret = win.run()
        win.hide()
        if ret == gtk.RESPONSE_ACCEPT:
            return True
        else:
            return None


if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = deal_editor_control(b)
    con.update_accounts([(1, "jfjfj"), (2, "ejfije")])
    con.run()
    print(con.get_updating_hash())
                               
        
