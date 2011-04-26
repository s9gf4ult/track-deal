#!/bin/env python
# -*- coding: utf-8 -*-
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sources
from modifying_tab_control import modifying_tab_control
import traceback
import sources

class deals_tab_controller(modifying_tab_control):
    def __init__(self, global_data, database, builder, update_callback, filter_control, adder_control, deal_editor, report_importer):
        self.builder = builder
        self.database = database
        self.filter = filter_control
        self.adder = adder_control
        self.deal_editor = deal_editor
        self.report_importer = report_importer
        self.global_data = global_data
        self.update_callback = update_callback
        def shorter(objname, signal, method):
            self.builder.get_object(objname).connect(signal, method)
        shorter("call_filter", "activate", self.call_filter_activate)
        shorter("delete_deals", "activate", self.delete_deals_activate)
        shorter("add_deal", "activate", self.add_deal_activate)
        shorter("update_deals_tab", "activate", self.update_deals_tab_activate)
        shorter("deals_load_open_ru", "activate", self.deals_load_open_ru_activate)
        shorter("change_deals", "activate", self.change_deals_activate)
        ############################
        # make columns in the view #
        ############################
        self.deals_view = list_view_sort_control(self.builder.get_object("deals_view"),
                                                 [(u"id", gtk.CellRendererSpin(), int, "id"),
                                                  (u'Дата', gtk.CellRendererText(), str, "datetime"),
                                                  (u'Время', gtk.CellRendererText(), str, "time"),
                                                  (u'Инструмент', gtk.CellRendererText(), str, "security_name"),
                                                  (u'Класс', gtk.CellRendererText(), str, "security_type"),
                                                  (u'Направление', gtk.CellRendererText(), str, "deal_sign"),
                                                  (u'Цена', gtk.CellRendererSpin(), float, "price"),
                                                  (u'Количество', gtk.CellRendererSpin(), int, "quantity"),
                                                  (u'Объем', gtk.CellRendererSpin(), float, "volume"),
                                                  (u'Комиссия брокера', gtk.CellRendererSpin(), float, "broker_comm"),
                                                  (u'Комиссия биржи', gtk.CellRendererSpin(), float, "stock_comm"),
                                                  (u'Тэги', gtk.CellRendererText(), str, "attributes")],
                                                 self_sorting = False,
                                                 sort_callback = self.sorted_callback)
        dd = self.builder.get_object("deals_view")
        dd.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        dd.connect("row-activated", self.deals_view_row_activated)
        self.sort_order = "id"

    def change_deals_activate(self, action):
        self.change_deals()

    def deals_view_row_activated(self, treeview, path, column):
        self.change_deals()

    def change_deals(self):
        d = self.builder.get_object("deals_view").get_selection().count_selected_rows()
        if d > 1:
            self.change_multiple_deals()
        elif d == 1:
            self.change_one_deal()

    def change_multiple_deals(self):
        d = self.builder.get_object("deals_view")
        (mod, paths) = d.get_selection().get_selected_rows()
        if paths != None and len(paths) > 1:
            dids = map(lambda it: mod.get_value(it, 0), map(lambda p: mod.get_iter(p), paths))
            self.deal_editor.update_accounts(self.database.connection.execute("select id, name from accounts").fetchall())
            self.deal_editor.update_instruments(map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals").fetchall()))
            self.deal_editor.update_markets(map(lambda a: a[0], self.database.connection.execute("select distinct security_type from deals").fetchall()))
            ret = self.deal_editor.run()
            if ret != None:
                dhash = self.deal_editor.get_updating_hash()
                if len(dhash) == 0:
                    return
                for did in dids:
                    self.database._update_from_hash("deals", did, dhash)
                self.call_update_callback()
            
            

    def change_one_deal(self):
        d = self.builder.get_object("deals_view")
        (mod, it) = d.get_selection().get_selected_rows()
        if it != None and len(it) == 1:
            dh = {}
            did = mod.get_value(mod.get_iter(it[0]), 0)
            for (val, key) in map(lambda a, b: (a, b),
                                  self.database.connection.execute("select datetime, deal_sign, account_id, security_name, security_type, price, quantity, broker_comm, stock_comm from deals where id = ?", (did, )).fetchone(),
                                  ["datetime", "deal_sign", "account_id", "security_name", "security_type", "price", "quantity", "broker_comm", "stock_comm"]):
                dh[key] = val
            dh["attributes"] = self.database.connection.execute("select name, value from deal_attributes where deal_id = ?", (did, )).fetchall()
            self.adder.update_widget(map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals order by security_name")),
                                     map(lambda a: a[0], self.database.connection.execute("select distinct security_type from deals order by security_type")),
                                     self.database.connection.execute("select id, name from accounts order by name").fetchall())
                                     
            self.adder.load_from_hash(dh)
            ret = self.adder.run()
            if ret != None:
                ret["id"] = did
                self.database.get_update_deal_from_hash(ret)
                self.call_update_callback()

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
            self.database.delete_deals_by_ids(map(lambda pth: model.get_value(model.get_iter(pth), 0), it))
            if gethash(self.global_data, "current_account") != None:
                self.database.delete_empty_positions()
                self.database.delete_broken_positions(self.global_data["current_account"])
                self.database.join_deals_leaves(self.global_data["current_account"])
                self.database.delete_empty_deal_groups()
                self.database.recalculate_position_attributes(self.global_data["current_account"])
            self.call_update_callback()
        dial.destroy()


    def add_deal_activate(self, action):
        self.add_deal()

    def add_deal(self):
        if not self.database.connection:
            return
        self.adder.update_widget(map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals order by security_name")),
                                 map(lambda a: a[0], self.database.connection.execute("select distinct security_type from deals order by security_type")),
                                 self.database.connection.execute("select id, name from accounts").fetchall())
        self.adder.set_current_datetime()
        self.adder.flush_attributes()
        ret = self.adder.run()
        if ret != None:
            self.database.get_from_list([ret])
            self.call_update_callback()


    def update_deals_tab_activate(self, action):
        self.update_widget()

    def deals_load_open_ru_activate(self, action):
        if self.database.connection != None:
            a = map(lambda a, b: (a, b), sources.classes.keys(), sources.classes.keys())
            self.report_importer.update_widget(accounts = self.database.connection.execute("select id, name from accounts").fetchall(),
                                               report_types = map(lambda a, b: (a, b), sources.classes.keys(), sources.classes.keys()))
            ret = self.report_importer.run()
            if ret != None:
                rt = self.report_importer.get_report_type()
                if isinstance(rt, str):
                    rt = rt.decode('utf-8')
                if gethash(sources.classes, rt) != None:
                    if sources.classes[rt] == sources.xml_parser:
                        self.load_open_ru(self.report_importer.get_account_id(), self.report_importer.get_file_name())
                

    def sorted_callback(self, column, order, params):
        if params != None:
            self.sort_order = params[0] + (order == gtk.SORT_DESCENDING and " desc" or "")
            self.update_widget()
        

    def load_open_ru(self, account, filename):
        if not self.database.connection:
            return
        try:
            xs = sources.xml_parser(filename)
            xs.check_file()
            self.database.get_from_source_in_account(account, xs)
            self.call_update_callback()
        except Exception as e:
            show_error(e.__str__(), self.builder.get_object("main_window"))
            print(traceback.format_exc())

    def call_filter_activate(self, action):
        self.call_filter()

    def call_filter(self):
        if not self.database.connection:
            return
        self.filter.run()
        self.update_widget()

    def update_widget(self):
        if not self.database.connection:
            self.deals_view.update_rows([])
            return
        self.filter._prepare_filter()
        self.filter._regen_selected()
        self.deals_view.update_rows(self.filter.get_ids(self.sort_order, fields = ["id", "formated_date", "formated_time", "security_name", "security_type", "buy_sell_formated", "price", "quantity", "volume", "broker_comm", "stock_comm", "attributes"]))
                
        
