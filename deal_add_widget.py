#/bin/env python
# -*- coding: utf-8 -*-

import gtk
from time_widget import time_widget
import time, datetime

class deal_add_widget:
    def __init__(self, parent = None):
        self.window = gtk.Dialog(title = u'Добавить сделку вручную', parent = parent, flags = gtk.DIALOG_MODAL, buttons = (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        t = gtk.Table(rows = 6, columns = 2)
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
        self.broker_comm = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        self.stock_comm = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        t.attach(self.broker_comm, left_attach = 1, right_attach = 2, top_attach = 5, bottom_attach = 6, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Вознаграждение брокера'), left_attach = 0, right_attach = 1, top_attach = 5, bottom_attach = 6, xoptions = gtk.FILL, yoptions = gtk.FILL)
        t.attach(self.stock_comm, left_attach = 1, right_attach = 2, top_attach = 6, bottom_attach = 7, yoptions = gtk.FILL)
        t.attach(gtk.Label(u'Вознаграждение биржи'), left_attach = 0, right_attach = 1, top_attach = 6, bottom_attach = 7, xoptions = gtk.FILL, yoptions = gtk.FILL)
        
                 
        self.window.get_content_area().pack_start(t)

    def update_widget(self, stock_list):
        dd = datetime.datetime.fromtimestamp(time.time())
        self.calendar.select_month(dd.month - 1, dd.year)
        self.calendar.select_day(dd.day)
        self.time.set_current_time()
        ii = self.stock_store.get_iter_first()
        while ii:
            self.stock_store.remove(ii)
            ii = self.stock_store.get_iter_first()
        for kava in stock_list:
            self.stock_store.append([kava])
        

    def run(self):
        self.window.show_all()
        ret = self.window.run()
        self.window.hide()
        return ret

    def get_datetime(self):
        dd = self.calendar.get_date()
        return datetime.datetime.combine(datetime.date(dd[0], dd[1] + 1, dd[2]), self.time.get_time())
        
        
if __name__ == "__main__":
    dial = deal_add_widget()
    dial.update_widget(["One", "Two", u"Чето там"])
    dial.run()
        
