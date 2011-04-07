#!/bin/env python
# -*- coding: utf-8 -*-
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sources

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
                                                 [(u"id", gtk.CellRendererSpin(), int, "id"),
                                                  (u'Время', gtk.CellRendererText(), str, "datetime"),
                                                  (u'Инструмент', gtk.CellRendererText(), str, "security_name"),
                                                  (u'Биржа', gtk.CellRendererText(), str, "security_type"),
                                                  (u'Направление', gtk.CellRendererText(), str, "deal_sign"),
                                                  (u'Цена', gtk.CellRendererSpin(), float, "price"),
                                                  (u'Количество', gtk.CellRendererSpin(), int, "quantity"),
                                                  (u'Объем', gtk.CellRendererSpin(), float, "volume"),
                                                  (u'Комиссия брокера', gtk.CellRendererSpin(), float, "broker_comm"),
                                                  (u'Комиссия биржи', gtk.CellRendererSpin(), float, "stock_comm")],
                                                 self_sorting = False,
                                                 sort_callback = self.sorted_callback)
        self.builder.get_object("deals_view").get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.sort_order = "id"

    def delete_deals_activate(self, action):
        self.delete_deals()

    def delete_deals(self):
        if not self.database.connection:
            return
        selected = self.builder.get_object("deals_view").get_selection()
        dial = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO, flags=gtk.DIALOG_MODAL, parent = self.builder.get_object("main_window"))
        dcount = selected.count_selected_rows()
        if dcount == 0:
            return
        dial.props.text = u'Удалить {0} сделок ? В любом случае это действие можно сразу отменить при помощи Rollback'.format(dcount)
        if dial.run() == gtk.RESPONSE_YES:
            (model, it) = selected.get_selected_rows()
            for ii in it:
                did = model.get_value(model.get_iter(ii), 0)
                self.database.connection.execute("delete from deals where id = ?", (did,))
            self.database.delete_empty_positions()
            self.database.delete_broken_positions()
            self.call_update_callback()
        dial.destroy()


    def add_deal_activate(self, action):
        self.add_deal()

    def add_deal(self):
        if not self.database.connection:
            return
        self.adder.update_widget(map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals order by security_name")),
                                      map(lambda a: a[0], self.database.connection.execute("select distinct security_type from deals order by security_type")))
        ret = self.adder.run()
        if ret != None:
            self.database.get_from_list([ret])
            self.call_update_callback()


    def update_deals_tab_activate(self, action):
        self.update_widget()

    def deals_load_open_ru_activate(self, action):
        self.load_open_ru()

    def sorted_callback(self, column, order, params):
        self.sort_order = params[0] + (order == gtk.SORT_DESCENDING and " desc" or "")
        self.update_widget()
        

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
                self.call_update_callback()
            except Exception as e:
                show_error(e.__str__(), win)
                print(traceback.format_exc())
        diag.destroy()
        fl.destroy()

    def call_update_callback(self):
        if self.update_callback:
            self.update_callback()
        else:
            self.update_widget()

    def call_filter_activate(self, action):
        self.call_filter()

    def call_filter(self):
        self.filter.run()
        self.update_widget()

    def update_widget(self):
        if not self.database.connection:
            return
        self.filter._prepare_filter()
        self.filter._regen_selected()
        self.filter._regen_boundary()
        l = []
        for x in self.filter.get_ids(self.sort_order, fields = ["id", "datetime", "security_name", "security_type", "deal_sign", "price", "quantity", "volume", "broker_comm", "stock_comm"]):
            r = list(x)
            if x[4] < 0:
                r[4] = "B"
            else:
                r[4] = "S"
            l.append(tuple(r))
        self.deals_view.update_rows(l)
                
        