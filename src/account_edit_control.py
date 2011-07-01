#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
from combo_control import combo_control
from common_methods import *

class account_edit_control:
    """
    \~russian
    \brief Контрол формы редактирования счета
    """
    ## name gtk.Entry
    name = None
    ## top window Gtk.Dialog instance
    window = None
    ## combo_control.combo_control instance with currency available to select
    currency_combo = None
    ## gtk.SpinButton instance with initial money amount
    first_money = None
    ## gtk.TextView instance with comment
    comment = None

    def set_comment(self, text):
        """\brief set comment field
        \param text
        """
        self.comment.set_text(text)

    def set_name(self, name):
        """\brief set name field
        \param name
        """
        self.name.set_text(name)

    def set_currency(self, currency):
        """\brief set currency field
        \param currency
        """
        self.currency_combo.set_value(currency)

    def set_first_money(self, money_amount):
        """\brief set money amount field
        \param money_amount
        """
        self.first_money.set_value(money_amount)

    
    def __init__(self, parent):
        self._parent = parent
        def shobject(name):
            return self._parent.builder.get_object(name)
        self.window = shobject("account_edit")
        self.window.set_transient_for(shobject("main_window"))
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.currency_combo = combo_control(shobject("account_edit_currency"))
        self.first_money = shobject("account_edit_money")
        self.first_money.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1, page_increment = 100)
        self.first_money.set_digits(4)
        self.name = shobject("account_edit_name")
        self.comment = shobject("account_edit_comment").get_buffer()
        shobject("account_edit_change").connect("clicked", self.change_clicked)

    def change_clicked(self, button):
        """\brief change currency button clicked handler
        \param button
        """
        if self._parent.currency.run() == gtk.RESPONSE_ACCEPT:
            self.update_currency()


    def update_widget(self, currencies):
        """
        \param currencies list of names of currencies
        """
        self.currency_combo.update_widget(currencies)

    def run(self):
        """\brief run the dialog
        \retval gtk.RESPONSE_ACCEPT save button pressed
        \retval gtk.RESPONSE_CANCEL cancel pressed
        """
        ret = self.window.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if not self.check_correctness():
                ret = self.window.run()
            else:
                self.window.hide()
                return ret
        self.window.hide()
        return ret
            
    def check_correctness(self):
        errs = []
        if len(self.name.get_text()) <= 0:
            errs.append(u'Необходимо указать имя счета')
        if self.first_money.get_value() <= 0:
            errs.append(u'Нужно указать не нулевой начальный счет')
        vv = self.currency_combo.get_value()
        if is_null_or_empty(vv):
            errs.append(u'Нужно указать название валюты')
        if len(errs) > 0:
            show_error(reduce(lambda a, b:u'{0}\n{1}'.format(a, b), errs), self.window)
            return False
        return True

    def get_data(self):
        """\brief return the data in dialog
        \return hash table with keys \c name, \c money_name, \c money_count and \c comment
        """
        ret = {'name' : self.name.get_text(),
               'money_count' : self.first_money.get_value(),
               'money_name' : self.currency_combo.get_value()}
        if self.comment.get_char_count() > 0:
            ret["comment"] = self.comment.get_text(self.comment.get_start_iter(), self.comment.get_end_iter())

        return ret

    def reset_widget(self, ):
        """\brief clear all fields and update currency combobox
        """
        self.clear_all()
        self.update_currency()

    def clear_all(self, ):
        """\brief clear all fields of widget
        """
        self.name.set_text("")
        self.comment.set_text("")
        self.currency_combo.set_value(None)
        self.currency_combo.update_widget([])
        self.first_money.set_value(0)

    def update_currency(self, ):
        """\brief update currency_combo with posible values
        """
        mm = self._parent.model.list_moneys()
        self.update_widget(map(lambda a: a["name"], mm))



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
