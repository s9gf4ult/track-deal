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
import gtk_view
from common_methods import *

class deal_editor_control:
    def __init__(self, parent):
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        self.builder = make_builder('glade/deal_editor.glade')
        def shorter(name):
            return self.builder.get_object(name)
        w = self.builder.get_object("deal_editor")
        w.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        
        ##########
        # hiders #
        ##########
        self.hiders = []
        for (hcb, box) in [("deal_editor_change_datetime", "deal_editor_datetime_box"),
                           ("deal_editor_change_direction", "deal_editor_direction_box"),
                           ("deal_editor_change_account", "deal_adder_account1"),
                           ("deal_editor_change_instrument", "deal_editor_instrument"),
                           ("deal_editor_change_price", "deal_adder_price1"),
                           ("deal_editor_change_count", "deal_adder_count1"),
                           ("deal_editor_change_commission", "deal_editor_commission")]:
            cb = self.builder.get_object(hcb)
            bb = self.builder.get_object(box)
            self.hiders.append(hide_control(cb, [bb]))
            pass

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

        self.instrument = combo_select_control(shorter("deal_editor_instrument"),
                                               checkbutton = shorter("deal_editor_change_instrument"))

        self.price = number_control(shorter("deal_adder_price1"), shorter("deal_editor_change_price"), step_incr = 0.1, digits = 4)
        self.count = number_control(shorter("deal_adder_count1"), shorter("deal_editor_change_count"))
        self.commission = number_control(shorter("deal_editor_commission"), shorter("deal_editor_change_commission"), step_incr = 0.1, digits = 4)
        for name in ["deal_adder_price1", "deal_adder_count1", "deal_editor_commission"]:
            m = shorter(name)
            m.get_adjustment().set_all(lower = 0, upper = sys.float_info.max)
        self.account = combo_select_control(shorter("deal_adder_account1"),
                                            checkbutton = shorter("deal_editor_change_account"))
        self.direction = select_control({-1 : shorter("deal_adder_buy_rb1"),
                                         1 : shorter("deal_adder_sell_rb1")}, shorter("deal_editor_change_direction"))


    def update_accounts(self):
        """accounts must be the list of tupples like this (account_id, account_name)"""
        if not self._parent.connected():
            return
        self.account.update_answers(map(lambda a: (a["id"], a["name"]), self._parent.model.list_accounts(["name"]))) 

    def update_instruments(self):
        """instruments is a list of strings"""
        if not self._parent.connected():
            return
        self.instrument.update_answers(map(lambda a: (a["id"], a["name"]), self._parent.model.list_papers(["name"])))

    def update_editor(self):
        """
        \brief update instrument and account list
        """
        self.update_instruments()
        self.update_accounts()
        
    def get_data(self):
        """\brief return data from dialog
        \return hash table with keys:\n
        \c datetime - datetime.datetime instance\n
        \c account_id - int, account id
        \c direction - -1 or 1\n
        \c paper_id - id of paper\n
        \c points - price in points\n
        \c count - count of contracts\n
        \c commission
        """
        ret = {}
        for (getter, key) in [(self.datetime.get_datetime, "datetime"),
                              (self.account.get_value, "account_id"),
                              (self.direction.get_value, "direction"),
                              (self.instrument.get_value, "paper_id"),
                              (self.price.get_value, "points"),
                              (self.count.get_value, "count"),
                              (self.commission.get_value, "commission")]:
            m = getter()
            if m != None:
                ret[key] = m
        return ret
        

    def run(self):
        """
        \retval gtk.RESPONSE_ACCEPT
        \retval gtk.RESPONSE_CANCEL
        """
        win = self.builder.get_object("deal_editor")
        win.show_all()
        ret = win.run()
        win.hide()
        return ret

if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('glade/deal_editor.glade')
    con = deal_editor_control(b)
    con.update_accounts([(1, "jfjfj"), (2, "ejfije")])
    con.run()
    print(con.get_data())
                               
        
