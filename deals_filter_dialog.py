#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from from_to_datetime_widget import from_to_datetime_widget
from hiding_checkbutton import hiding_checkbutton
from check_widget import check_widget
from select_widget import select_widget
from from_to_integer_widget import from_to_integer_widget

class deals_filter_dialog():

    def __init__(self, parent = None, modal = True):
        self.window = gtk.Dialog(title = u'Фильтр сделок', parent = parent, flags = (modal and gtk.DIALOG_MODAL or 0), buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.notebook = gtk.Notebook()
        vbox = self.window.get_content_area()
        vbox.pack_start(self.notebook, True)
        self.date_selector = from_to_datetime_widget(u'Учитывать дату сделки', vertical = False, expand = True, hide = False)
        self.notebook.insert_page(self.date_selector.get_widget(), tab_label= gtk.Label(u'Дата'))
        self.stock_check = check_widget(u'Инструмент')
        self.notebook.insert_page(self.stock_check.get_widget(), tab_label = gtk.Label(u'Инструменты'))
        vbox2 = gtk.VBox()
        self.is_position = select_widget(u'Позиция', {True : u'Сделка приписана к позиции', False : u'Сделка свободна'}, vertical = False, expand = False, hide = False)
        vbox2.pack_start(self.is_position.get_widget(), False)
        self.direction = select_widget(u'Направление сделки', {-1 : u'Покупка', 1 : u'Продажа'}, vertical = False, expand = False, hide = False)
        vbox2.pack_start(self.direction.get_widget(), False)
        self.price_range = from_to_integer_widget(u'Цена сделки', gtk.Adjustment(step_incr = 0.01), gtk.Adjustment(step_incr = 0.01), vertical = False, expand = False, digits=4, hide = False)
        self.price_range.to_hide = True
        vbox2.pack_start(self.price_range.get_widget(), False)
        self.count_range = from_to_integer_widget(u'Количество контрактов', gtk.Adjustment(step_incr = 1), gtk.Adjustment(step_incr = 1), vertical = False, expand = False, hide = False)
        self.count_range.to_hide = True
        vbox2.pack_start(self.count_range.get_widget(), False)
        self.commission = from_to_integer_widget(u'Коммиссия', gtk.Adjustment(step_incr = 0.01), gtk.Adjustment(step_incr = 0.01), vertical = False, expand = False, digits = 2, hide = False)
        self.commission.to_hide = True
        vbox2.pack_start(self.commission.get_widget(), False)
        self.notebook.insert_page(vbox2, tab_label = gtk.Label(u'Другое'))
        
    def update_widget(self, stock_list = None, min_max_price = None, min_max_count = None, min_max_commission = None):
        if stock_list:
            self.stock_check.update_widget(stock_list)

        for (min_max, _range) in [(min_max_price, self.price_range),
                                        (min_max_count, self.count_range),
                                        (min_max_commission, self.commission)]:
            _range.update_widget(min_max)


    def run(self):
        self.window.show_all()
        ret = self.window.run()
        self.window.hide()
        return ret

    
if __name__ == "__main__":
    df = deals_filter_dialog()
    df.run()
