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
                                                      shorter("deal_adder_sec1"))
                                         shorter("deal_editor_change_datetime"))

        self.instrument = combo_control(shorter("deal_adder_stock1"),
                                        shorter("deal_editor_change_instrument"))

        self.market = combo_control(shorter("deal_adder_market1"),
                                    shorter("deal_editor_cnahge_stock"))

        self.price = number_control(shorter("deal_adder_price1"), shorter("deal_editor_change_price"))
        self.count = number_control(shorter("deal_adder_count1"), shorter("deal_editor_change_count"))
        self.broker_comm = number_control(shorter("deal_adder_broker_comm1"), shorter("deal_editor_change_broker_comm"))
        self.stock_comm = number_control(shorter("deal_adder_stock_comm1"), shorter("deal_editor_change_stock_comm"))
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
                               
        

    def run(self):
        self.builder.get_object("deal_editor").run()


if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = deal_editor_control(b)
    con.run()
                               
        
