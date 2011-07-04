#!/bin/env python
# -*- coding: utf-8 -*-
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sources

class deals_tab_controller(object):
    def __init__(self, parent):
        self._parent = parent
        def shorter(objname, signal, method):
            self._parent.builder.get_object(objname).connect(signal, method)
        shorter("call_filter", "activate", self.call_filter_activate)
        shorter("delete_deals", "activate", self.delete_deals_activate)
        shorter("add_deal", "activate", self.add_deal_activate)
        shorter("update_deals_tab", "activate", self.update_deals_tab_activate)
        shorter("deals_load_open_ru", "activate", self.deals_load_open_ru_activate)
        shorter("change_deals", "activate", self.change_deals_activate)
        ############################
        # make columns in the view #
        ############################
        self.deals_view = list_view_sort_control(self._parent.builder.get_object("deals_view"),
                                                 [(u"id", gtk.CellRendererSpin(), int, "id"),
                                                  (u'Дата', gtk.CellRendererText(), str, "datetime"),
                                                  (u'Время', gtk.CellRendererText(), str, "time"),
                                                  (u'Инструмент', gtk.CellRendererText(), str, "security_name"),
                                                  (u'Класс', gtk.CellRendererText(), str, "security_type"),
                                                  (u'Направление', gtk.CellRendererText(), str, "deal_sign"),
                                                  (u'Цена', gtk.CellRendererSpin(), float, "price"),
                                                  (u'Количество', gtk.CellRendererSpin(), int, "quantity"),
                                                  (u'Объем', gtk.CellRendererSpin(), float, "volume"),
                                                  (u'Комиссия', gtk.CellRendererSpin(), float, "broker_comm"),
                                                  (u'Тэги', gtk.CellRendererText(), str, "attributes")],
                                                 self_sorting = False,
                                                 sort_callback = self.sorted_callback)
        dd = self._parent.builder.get_object("deals_view")
        dd.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        dd.connect("row-activated", self.deals_view_row_activated)
        self.sort_order = "id"

    def change_deals_activate(self, action):
        self.change_deals()

    def deals_view_row_activated(self, treeview, path, column):
        self.change_deals()

    def change_deals(self):
        if not self._parent.connected():
            return
        d = self._parent.builder.get_object("deals_view").get_selection().count_selected_rows()
        if d > 1:
            self.change_multiple_deals()
        elif d == 1:
            self.change_one_deal()
            
    def change_multiple_deals(self):
        if not self._parent.connected():
            return
        d = self._parent.builder.get_object("deals_view")
        (mod, paths) = d.get_selection().get_selected_rows()
        if paths != None and len(paths) > 1:
            dids = map(lambda it: mod.get_value(it, 0), map(lambda p: mod.get_iter(p), paths))
            self._parent.deal_editor.update_editor()
            ret = self._parent.deal_editor.run()
            if ret == gtk.RESPONSE_ACCEPT:
                dhash = self.deal_editor.get_data()
                if is_null_or_empty(dhash):
                    return
                self._parent.model.tachange_deals(dids, dhash)
                self._parent.call_update_callback()
            
            

    def change_one_deal(self):
        if not self._parent.connected():
            return
        row = self.deals_view.get_selected_rows()
        if not is_null_or_empty(row) and len(row) == 1:
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
        selected = self._parent.builder.get_object("deals_view").get_selection()
        dial = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO, flags=gtk.DIALOG_MODAL, parent = self._parent.builder.get_object("main_window"))
        dcount = selected.count_selected_rows()
        if dcount == 0:
            return
        dial.props.text = u'Удалить {0} сделок ? В любом случае это действие можно сразу отменить'.format(dcount)
        if dial.run() == gtk.RESPONSE_YES:
            (model, it) = selected.get_selected_rows()
            self._parent.model.taremove_deal(map(lambda pth: model.get_value(model.get_iter(pth), 0), it))
            self._parent.call_update_callback()
        dial.destroy()


    def add_deal_activate(self, action):
        self.add_deal()

    def add_deal(self):
        """
        \brief run dialog and save deal to database if "save" pressed
        """
        if not self._parent.connected():
            return
        self._parent.deal_adder.reset_fields() # clean all fields
        self._parent.deal_adder.update_widget() # set the posible accounts and so on
        self._parent.deal_adder.set_current_datetime()
        ret = self._parent.deal_adder.run()
        if ret == gtk.RESPONSE_YES:
            data = self._parent.deal_adder.get_data()
            self._parent.model.tacreate_deal(data["account_id"], data)
            self._parent.call_update_callback()


    def update_deals_tab_activate(self, action):
        self.update()

    def deals_load_open_ru_activate(self, action):
        if not self._parent.connected():
            return
        self._parent.report_importer.update_importer()
        ret = self._parent.report_importer.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.call_update_callback()
                

    def sorted_callback(self, column, order, params):
        if params != None:
            self.sort_order = params[0] + (order == gtk.SORT_DESCENDING and " desc" or "")
            self.update()
        

    def load_open_ru(self, account, filename):
        if not self._parent.connected():
            return
        try:
            xs = sources.xml_parser(filename)
            xs.check_file()
            self._parent.model.get_from_source_in_account(account, xs)
            self._parent.call_update_callback()
        except Exception as e:
            show_error(e.__str__(), self._parent.builder.get_object("main_window"))
            print(traceback.format_exc())

    def call_filter_activate(self, action):
        self.call_filter()

    def call_filter(self):
        if not self._parent.connected():
            return
        self._parent.deals_filter.run()
        self._parent.call_update_callback()

    def update(self):
        if not self._parent.connected():
            self.deals_view.make_model() # clean list of deals
            return
        self._parent.deals_filter.update_filter()
        self.deals_view.update_rows(map(lambda a: (a["deal_id"], a["date_formated"], a["time_formated"], a["paper_name"], a["paper_class"], a["direction_formated"], a["price_formated"], a["count"], a["volume_formated"], a["commission"], a["user_attributes_formated"]),  self._parent.deals_filter.get_rows(self.sort_order)))
                
        
