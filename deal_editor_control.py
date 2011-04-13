#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import *
import sys

class deal_editor_control:
    def __init__(self, builder):
        self.builder = builder

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

        

    def run(self):
        self.builder.get_object("deal_editor").run()


if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = deal_editor_control(b)
    con.run()
                               
        
