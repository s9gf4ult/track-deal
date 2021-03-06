#!/bin/env python
# -*- coding: utf-8 -*-
from common_methods import is_null_or_empty, show_error, format_number
from list_view_sort_control import list_view_sort_control
from loader_dialog import loader_dialog
from od_exceptions import od_exception_config_key_error
import gtk
import sources
import traceback

class deals_tab_controller(object):
    def __init__(self, parent):
        self._parent = parent
        def shorter(objname, signal, method):
            self._parent.window.builder.get_object(objname).connect(signal, method)
        self.loader_dialog = loader_dialog(self._parent)
        shorter("call_filter", "activate", self.call_filter_activate)
        shorter("delete_deals", "activate", self.delete_deals_activate)
        shorter("add_deal", "activate", self.add_deal_activate)
        shorter("update_deals_tab", "activate", self.update_deals_tab_activate)
        shorter("deals_load_open_ru", "activate", self.deals_load_open_ru_activate)
        shorter("change_deals", "activate", self.change_deals_activate)
        ############################
        # make columns in the view #
        ############################
        self.deals_view = list_view_sort_control(self._parent.window.builder.get_object("deals_view"),
                                                 [[u"id", int],
                                                  (u'Дата', gtk.CellRendererText(), str, "datetime"),
                                                  (u'Время', gtk.CellRendererText(), str, "time"),
                                                  (u'Инструмент', gtk.CellRendererText(), str, "paper_name"),
                                                  (u'Направление', gtk.CellRendererText(), str, "direction"),
                                                  (u'Цена', gtk.CellRendererText(), str, "price"),
                                                  (u'Количество', gtk.CellRendererSpin(), int, "count"),
                                                  (u'Объем', gtk.CellRendererText(), str, "volume"),
                                                  (u'Net Bfr.', gtk.CellRendererText(), str, 'net_before'),
                                                  (u'Net Aftr.', gtk.CellRendererText(), str, 'net_after'),
                                                  (u'Комиссия', gtk.CellRendererText(), str, "commission"),
                                                  (u'Тэги', gtk.CellRendererText(), str, "user_attributes_formated")],
                                                 self_sorting = False,
                                                 sort_callback = self.sorted_callback)
        dd = self._parent.window.builder.get_object("deals_view")
        dd.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        dd.connect("row-activated", self.deals_view_row_activated)
        self.sort_order = ["deal_id"]

    def change_deals_activate(self, action):
        self.change_deals()

    def deals_view_row_activated(self, treeview, path, column):
        self.change_deals()

    def change_deals(self):
        if not self._parent.connected():
            return
        d = self._parent.window.builder.get_object("deals_view").get_selection().count_selected_rows()
        if d > 1:
            self.change_multiple_deals()
        elif d == 1:
            self.change_one_deal()
            
    def change_multiple_deals(self):
        if not self._parent.connected():
            return
        selected = self.deals_view.get_selected_rows()
        self._parent.deal_editor.update_editor()
        ret = self._parent.deal_editor.run()
        if ret == gtk.RESPONSE_ACCEPT:
            dhash = self._parent.deal_editor.get_data()
            if is_null_or_empty(dhash):
                return
            self._parent.model.tachange_deals(map(lambda dl: dl[0], selected), dhash)
            self._parent.call_update_callback()
            
    def change_one_deal(self):
        if not self._parent.connected():
            return
        row = self.deals_view.get_selected_rows()
        if not is_null_or_empty(row) and len(row) == 1:
            self._parent.deal_adder.update_adder()
            self._parent.deal_adder.load_from_deal(row[0][0])
            ret = self._parent.deal_adder.run()
            if ret == gtk.RESPONSE_ACCEPT:
                data = self._parent.deal_adder.get_data()
                self._parent.model.tachange_deals(row[0][0], data)
                self._parent.call_update_callback()
        
    def delete_deals_activate(self, action):
        self.delete_deals()

    def delete_deals(self):
        """
        \brief remove selected deals from the database and call update
        """
        if not self._parent.connected():
            return
        selected = self.deals_view.get_selected_rows()
        if len(selected) > 0:
            self._parent.model.taremove_deal(map(lambda dl: dl[0], selected))
            self._parent.call_update_callback()
        
    def add_deal_activate(self, action):
        self.add_deal()

    def add_deal(self):
        """
        \brief run dialog and save deal to database if "save" pressed
        """
        if not self._parent.connected():
            return
        self._parent.deal_adder.reset_fields() # clean all fields
        self._parent.deal_adder.update_adder() # set the posible accounts and so on
        self._parent.deal_adder.set_current_datetime()
        ret = self._parent.deal_adder.run()
        if ret == gtk.RESPONSE_ACCEPT:
            data = self._parent.deal_adder.get_data()
            self._parent.model.tacreate_deal(data["account_id"], data)
            self._parent.call_update_callback()


    def update_deals_tab_activate(self, action):
        self.update()

    def deals_load_open_ru_activate(self, action):
        if not self._parent.connected():
            return
        ret = self.loader_dialog.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.call_update_callback()

    def sorted_callback(self, column, order, params):
        if params != None:
            self.sort_order = [params[0] + (order == gtk.SORT_DESCENDING and " desc" or "")]
            self.update()
        

    def load_open_ru(self, account, filename):
        if not self._parent.connected():
            return
        try:
            xs = sources.open_ru_report_source(filename)
            xs.check_file()
            self._parent.model.get_from_source_in_account(account, xs)
            self._parent.call_update_callback()
        except Exception as e:
            show_error(e.__str__(), self._parent.window.builder.get_object("main_window"))
            print(traceback.format_exc())

    def call_filter_activate(self, action):
        self.call_filter()

    def call_filter(self):
        if not self._parent.connected():
            return
        self._parent.deals_filter.prepare_filter()
        self._parent.deals_filter.run()
        self._parent.call_update_callback()

    def update(self):
        try:
            self.deals_view.set_odd_color(self._parent.settings.get_key('interface.odd_color'))
            self.deals_view.set_even_color(self._parent.settings.get_key('interface.even_color'))
        except od_exception_config_key_error:
            pass
        if not self._parent.connected():
            self.deals_view.make_model() # clean list of deals
            return
        self._parent.deals_filter.prepare_filter()
        self.deals_view.update_rows(map(lambda a: (a["deal_id"], a["date_formated"], a["time_formated"], a["paper_name"], a["direction_formated"], a["price_formated"], a["count"], a["volume_formated"], format_number(a['net_before']), format_number(a['net_after']), format_number(a["commission"]), a["user_attributes_formated"]),  self._parent.deals_filter.get_data(self.sort_order)))
                
        
