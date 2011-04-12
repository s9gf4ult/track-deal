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
        ret = self.window.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if not self.check_correctness():
                ret = self.window.run()
            else:
                self.window.hide()
                return self.get_data()
        self.window.hide()
        return None
            
    def check_correctness(self):
        errs = []
        if len(self.name.get_text()) <= 0:
            errs.append(u'Необходимо указать имя счета')
        if self.first_money.get_value() <= 0:
            errs.append(u'Нужно указать не нулевой начальный счет')
        vv = self.currency_combo.get_value()
        if vv == None or len(vv) <= 0:
            errs.append(u'Нужно указать название валюты')
        if len(errs) > 0:
            show_error(reduce(lambda a, b:u'{0}\n{1}'.format(a, b), errs), self.window)
            return False
        return True

    def get_data(self):
        ret = {'name' : self.name.get_text(),
               'first_money' : self.first_money.get_value(),
               'currency' : self.currency_combo.get_value()}
        return ret

    def load_to_widget(self, data):
        if data.has_key("name"):
            self.name.set_text(data['name'])

        if data.has_key("first_money"):
            self.first_money.set_value(data['first_money'])

        if data.has_key('currency'):
            self.currency_combo.set_value(data['currency'])
        
        
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = account_edit_control(b)
    con.update_widget(['RUB', 'EURO', 'DOLLAR'])
    print(con.run())
