#!/bin/env python
# -*- coding: utf-8 -*-

from deal_add_widget import deal_add_widget
import gtk

class deal_adder:
    def __init__(self, database, parent = None):
        self.dialog = deal_add_widget(parent = parent)
        self.database = database


    def run(self):
        if not self.database.connection:
            return None
        stocks = map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals").fetchall())
        self.dialog.update_widget(stocks)
        if self.dialog.run() == gtk.RESPONSE_ACCEPT:
            self.database._insert_from_hash("deals", {"security_name" : self.dialog.stock_combo.get_active_text(),
                                                      "datetime" : self.dialog.get_datetime(),
                                                      "price" : self.dialog.price.get_value(),
                                                      "quantity" : self.dialog.count.get_value_as_int(),
                                                      "volume" : self.dialog.price.get_value() * self.dialog.count.get_value_as_int(),
                                                      "broker_comm" : self.dialog.broker_comm.get_value(),
                                                      "stock_comm" : self.dialog.stock_comm.get_value(),
                                                      "broker_comm_nds" : 0,
                                                      "stock_comm_nds" : 0,
                                                      "deal_sign" : self.dialog.radio_buy.get_active() and -1 or 1})
            
        
                 
