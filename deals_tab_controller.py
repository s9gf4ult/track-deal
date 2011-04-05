#!/bin/env python
# -*- coding: utf-8 -*-
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *

class deals_tab_controller:
    def __init__(self, database, builder, update_callback, filter_control, adder_control):
        self.builder = builder
        self.database = database
        self.filter = filter_control
        self.adder = adder_control
        self.update_callback = update_callback
        def shorter(objname, signal, method):
            self.builder.get_object(objname).connect(signal, method)
        shorter("call_filter", "activate", self.call_filter_activate)
        shorter("delete_deals", "activate", self.delete_deals_activate)
        shorter("add_deal", "activate", self.add_deal_activate)
        shorter("update_deals_tab", "activate", self.update_deals_tab_activate)
        shorter("deals_load_open_ru", "activate", self.deals_load_open_ru_activate)
        ############################
        # make columns in the view #
        ############################
        self.deals_view = list_view_sort_control(self.builder.get_object("deals_view"),
                                                 [(u"id", gtk.CellRendererText()),
                                                  (u'Время', gtk.CellRendererText()),
                                                  (u'Инструмент', gtk.CellRendererText()),
                                                  (u'Биржа', gtk.CellRendererText()),
                                                  (u'Направление', gtk.CellRendererText()),
                                                  (u'Цена', gtk.CellRendererText()),
                                                  (u'Количество', gtk.CellRendererText()),
                                                  (u'Объем', gtk.CellRendererText()),
                                                  (u'Комиссия брокера', gtk.CellRendererText()),
                                                  (u'Комиссия биржи', gtk.CellRendererText())])

    def delete_deals_activate(self, action):
        pass

    def add_deal_activate(self, action):
        pass

    def update_deals_tab_activate(self, action):
        self.update_widget()

    def deals_load_open_ru_activate(self, action):
        self.load_open_ru()

    def load_open_ru(self):
        if not self.database.connection:
            return
        win = self.builder.get_object("main_window")
        diag = gtk.FileChooserDialog(title = u'Открыть отчет "Открытие"', parent = win, action = gtk.FILE_CHOOSER_ACTION_OPEN)
        diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
        fl = gtk.FileFilter()
        fl.add_mime_type('application/xml')
        diag.set_filter(fl)
        if diag.run() == gtk.RESPONSE_ACCEPT:
            try:
                xs = sources.xml_parser(diag.get_filename())
                xs.check_file()
                self.database.get_from_source(xs)
            except Exception as e:
                self.show_error(e.__str__())
                print(traceback.format_exc())
        diag.destroy()
        fl.destroy()
        self.update_widget()


    def call_filter_activate(self, action):
        self.call_filter()

    def call_filter(self):
        self.filter.run()
        self.update_widget()
        if self.update_callback:
            self.update_callback()

    def update_widget(self):
        if not self.database.connection:
            return
        l = []
        for x in self.filter.get_ids(None, fields = ["id", "datetime", "security_name", "security_type", "deal_sign", "price", "quantity", "volume", "broker_comm", "stock_comm"]):
            if x[4] < 0:
                x[4] = "B"
            else:
                x[4] = "S"
            l.append(x)
        self.deals_view.update_rows(l)
                
        
