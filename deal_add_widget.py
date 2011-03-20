#/bin/env python
# -*- coding: utf-8 -*-

import gtk
from time_widget import time_widget

class deal_add_widget:
    def __init__(self, parent = None):
        self.window = gtk.Dialog(title = u'Добавить сделку вручную', parent = parent, flags = gtk.DIALOG_MODAL, buttons = (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        t = gtk.Table(rows = 4, columns = 2)
        t.set_col_spacing(0, 10)
        self.calendar = gtk.Calendar()
        self.time = time_widget()
        v = gtk.VBox()
        v.pack_start(self.calendar)
        v.pack_start(self.time.get_widget(), False)
        t.attach(v, left_attach = 1, right_attach = 2, top_attach = 0, bottom_attach = 1)
        t.attach(gtk.Label(u'Дата и время'), left_attach = 0, right_attach = 1, top_attach = 0, bottom_attach = 1, xoptions = gtk.FILL, yoptions = gtk.FILL)
        self.stock_store = gtk.ListStore(str)
        self.stock_combo = gtk.ComboBoxEntry(model = self.stock_store, column = 0)
        t.attach(self.stock_combo, left_attach = 1, right_attach = 2, top_attach = 1, bottom_attach = 2, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Инструмент'), left_attach = 0, right_attach = 1, top_attach = 1, bottom_attach = 2, xoptions = gtk.FILL, yoptions = gtk.FILL)
        self.count = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 1), climb_rate = 0.01)
        t.attach(self.count, left_attach = 1, right_attach = 2, top_attach = 2, bottom_attach = 3, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Количество'), left_attach = 0, right_attach = 1, top_attach = 2, bottom_attach = 3, xoptions = gtk.FILL, yoptions = gtk.FILL)
        self.price = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        t.attach(self.price, left_attach = 1, right_attach = 2, top_attach = 3, bottom_attach = 4, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Цена'), left_attach = 0, right_attach = 1, top_attach = 3, bottom_attach = 4, xoptions = gtk.FILL, yoptions = gtk.FILL)
        self.radio_buy = gtk.RadioButton(label = u'Купить')
        self.radio_sell = gtk.RadioButton(group = self.radio_buy, label = u'Продать')
        v = gtk.HBox()
        v.pack_start(self.radio_buy, False)
        v.pack_start(self.radio_sell, False)
        t.attach(v, left_attach = 1, right_attach = 2, top_attach = 4, bottom_attach = 5, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Направление'), left_attach = 0, right_attach = 1, top_attach = 4, bottom_attach = 5, xoptions = gtk.FILL, yoptions = gtk.FILL)
        self.window.get_content_area().pack_start(t)

    def update_widget(self, stock_list, 

    def run(self):
        self.window.show_all()
        ret = self.window.run()
        self.window.hide()
        return ret
        
        
if __name__ == "__main__":
    dial = deal_add_widget()
    dial.run()
        
