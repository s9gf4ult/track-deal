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
        self.window = gtk.Window()
        self.window.set_border_width(5)
        if parent:
            self.window.set_transient_for(parent)
        self.window.set_modal(modal)
        self.close = gtk.Button(stock = gtk.STOCK_CLOSE)
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.pack_start(self.close, padding = 3)
        self.notebook = gtk.Notebook()
        vbox = gtk.VBox()
        vbox.pack_start(self.notebook, True)
        vbox.pack_start(bbox, False, padding = 3)
        self.window.add(vbox)
        self.date_selector = from_to_datetime_widget(u'Учитывать дату сделки', vertical = False, expand = True)
        self.notebook.insert_page(self.date_selector.get_widget(), tab_label= gtk.Label(u'Дата'))
        self.stock_check = check_widget(u'Инструмент')
        self.notebook.insert_page(self.stock_check.get_widget(), tab_label = gtk.Label(u'Инструменты'))
        vbox2 = gtk.VBox()
        self.is_position = select_widget(u'Позиция', {True : u'Сделка приписана к позиции', False : u'Сделка свободна'}, vertical = False, expand = True)
        vbox2.pack_start(self.is_position.get_widget(), False)
        self.price_diap = from_to_integer_widget(u'Цена сделки', None, None, vertical = False, expand = True, digits=2)
        vbox2.pack_start(self.price_diap.get_widget(), False)
        self.count_diap = from_to_integer_widget(u'Количество контрактов', None, None, vertical = False, expand = True)
        vbox2.pack_start(self.count_diap.get_widget(), False)
        self.direction = select_widget(u'Направление сделки', {-1 : u'Покупка', 1 : u'Продажа'}, vertical = False, expand = True)
        vbox2.pack_start(self.direction.get_widget(), False)
        self.commission = from_to_integer_widget(u'Коммиссия', None, None, vertical = False, expand = True)
        
        
        self.notebook.insert_page(vbox2, tab_label = gtk.Label(u'Другое'))

    def show(self):
        self.window.show_all()

    
if __name__ == "__main__":
    df = deals_filter_dialog()
    df.show()
    gtk.main()
