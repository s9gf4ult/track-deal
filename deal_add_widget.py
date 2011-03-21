#/bin/env python
# -*- coding: utf-8 -*-

import gtk
from time_widget import time_widget
import time, datetime
import vertical_table_pack

class deal_add_widget:
    def __init__(self, parent = None):
        self.window = gtk.Dialog(title = u'Добавить сделку вручную', parent = parent, flags = gtk.DIALOG_MODAL, buttons = (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.calendar = gtk.Calendar()
        self.time = time_widget()
        v = gtk.VBox()
        v.pack_start(self.calendar)
        v.pack_start(self.time.get_widget(), False)
        pack = [(u'Дата и время', v)]
        
        self.stock_store = gtk.ListStore(str)
        self.stock_combo = gtk.ComboBoxEntry(model = self.stock_store, column = 0)
        pack.append((u'Инструмент', self.stock_combo))
        self.count = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 1), climb_rate = 0.01)
        pack.append((u'Количество', self.count))
        self.price = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        pack.append((u'Цена', self.price))
        self.radio_buy = gtk.RadioButton(label = u'Купить')
        self.radio_sell = gtk.RadioButton(group = self.radio_buy, label = u'Продать')
        v = gtk.HBox()
        v.pack_start(self.radio_buy, False)
        v.pack_start(self.radio_sell, False)
        pack.append((u'Направление', v))
        self.broker_comm = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        self.stock_comm = gtk.SpinButton(adjustment = gtk.Adjustment(lower = 0, upper = 999999999, step_incr = 0.01), climb_rate = 0.01, digits = 4)
        pack += [(u'Вознаграждение брокера', self.broker_comm), (u'Комиссия биржи', self.stock_comm)]
        t = vertical_table_pack.pack_vertical(map(lambda a: [gtk.Label(a[0])] + list(a[1:]), pack), expandingrow = 0, expandingcol = 1)
                 
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
        
