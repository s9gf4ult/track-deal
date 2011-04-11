#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
from combo_control import combo_control
from common_methods import *

class account_edit_control:
    def __init__(self, builder):
        self.builder = builder
        def shobject(name):
            return self.builder.get_object(name)
        self.window = shobject("account_edit")
        self.window.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.currency_combo = combo_control(shobject("account_edit_currency"))
        self.first_money = shobject("account_edit_money")
        self.first_money.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1, page_increment = 100)
        self.first_money.set_digits(4)
        self.name = shobject("account_edit_name")

    def update_widget(self, currencies):
        self.currency_combo.update_widget(currencies)

    def run(self):
        
        
