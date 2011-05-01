#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import *
import gtk
from common_methods import *

class positions_tab_controller(modifying_tab_control):
    order_by = None
    def __init__(self, global_data, database, builder, pfilter, position_adder, update_callback):
        self.database = database
        self.builder = builder
        self.pfilter = pfilter
        self.global_data = global_data
        self.position_adder = position_adder
        self.update_callback = update_callback
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)
        self.positions_list = list_view_sort_control(self.builder.get_object("positions_view"),
                                                     [(u'id', gtk.CellRendererSpin(), int, u'id'),
                                                      (u'Дата Откр.', gtk.CellRendererText(), str, u'open_datetime'),
                                                      (u'время Откр.', gtk.CellRendererText(), str, u'open_time'),
                                                      (u'Дата Закр.', gtk.CellRendererText(), str, u'close_datetime'),
                                                      (u'Время Закр.', gtk.CellRendererText(), str, u'close_time'),
                                                      (u'В позиции', gtk.CellRendererText(), str, u'duration'),
                                                      (u'Тикер', gtk.CellRendererText(), str, u'ticket'),
                                                      (u'Кол-во', gtk.CellRendererSpin(), int, u'count'),
                                                      (u'Тип', gtk.CellRendererText(), str, u'direction'),
                                                      (u'Цена Откр.', gtk.CellRendererSpin(), float, u'open_coast'),
                                                      (u'Цена Закр.', gtk.CellRendererSpin(), float, u'close_coast'),
                                                      (u'Ход', gtk.CellRendererText(), str, u'coast_range'),
                                                      (u'Gross Bfr.', gtk.CellRendererSpin(), float, u'gross_before'),
                                                      (u'Gross Aftr.', gtk.CellRendererSpin(), float, u'gross_after'),
                                                      (u'P/L Gross', gtk.CellRendererText(), str, u'pl_gross_range'),
                                                      (u'Net Bfr.', gtk.CellRendererSpin(), float, u'net_before'),
                                                      (u'Net Aftr.', gtk.CellRendererSpin(), float, u'net_after'),
                                                      (u'P/L Net', gtk.CellRendererText(), str, u'pl_net_range'),
                                                      (u'% Изменения', gtk.CellRendererText(), str, u'plnet_acc')],
                                                     self_sorting = False,
                                                     sort_callback = self.sort_callback)
        self.builder.get_object("positions_view").get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        shorter("positions_make", "activate", self.make_positions_activate)
        shorter("call_positions_filter", "activate", self.filter_activate)
        shorter("delete_positions", "activate", self.delete_positions_activate)
        shorter("add_position", "activate", self.add_position_activate)
        shorter("update_positions", "activate", self.update_positions_activate)

    def update_positions_activate(self, action):
        self.update_positions()

    def update_positions(self):
        if self.database.connection == None or gethash(self.global_data, "current_account") == None:
            return
        self.database.delete_empty_positions()
        self.database.delete_broken_positions(self.global_data["current_account"])
        self.update_widget()

    def add_position_activate(self, action):
        self.add_position()

    def add_position(self):
        if self.database.connection == None or gethash(self.global_data, "current_account") == None:
            return
        self.position_adder.update_instruments(self.database.get_instruments())
        self.position_adder.update_classes(self.database.get_classes())
        ret = self.position_adder.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self.database.add_position(self.global_data["current_account"],
                                       self.position_adder.instrument.get_value(),
                                       self.position_adder.instrument_class.get_value(),
                                       self.position_adder.long_short.get_value(),
                                       self.position_adder.count.get_value(),
                                       {"date" : self.position_adder.start_date.get_datetime(),
                                        "price" : self.position_adder.price.get_lower_value(),
                                        "broker_comm" : self.position_adder.broker_comm.get_lower_value(),
                                        "stock_comm" : self.position_adder.stock_comm.get_lower_value()},
                                       {"date" : self.position_adder.end_date.get_datetime(),
                                        "price" : self.position_adder.price.get_upper_value(),
                                        "broker_comm" : self.position_adder.broker_comm.get_upper_value(),
                                        "stock_comm" : self.position_adder.stock_comm.get_upper_value()})
            self.database.recalculate_position_attributes(self.global_data["current_account"])
            self.call_update_callback()

    def delete_positions_activate(self, action):
        self.delete_positions()

    def delete_positions(self):
        if self.database.connection == None:
            return
        (model, paths) = self.builder.get_object("positions_view").get_selection().get_selected_rows()
        if len(paths) > 0:
            itrs = map(lambda pt: model.get_iter(pt), paths)
            try:
                self.database.delete_positions_by_ids(map(lambda itr: model.get_value(itr, 0), itrs))
                if gethash(self.global_data, "current_account") != None:
                    self.database.join_deals_leaves(self.global_data["current_account"])
                    self.database.delete_empty_deal_groups()
                    self.database.recalculate_position_attributes(self.global_data["current_account"])
                self.call_update_callback()
            except Exception as e:
                show_and_print_error(e, self.builder.get_object("main_window"))

    def make_positions_activate(self, action):
        self.make_positions()

    def make_positions(self):
        if self.database.connection != None and gethash(self.global_data, "current_account") != None:
            self.database.make_positions_in_account(self.global_data["current_account"])
            self.database.recalculate_position_attributes(self.global_data["current_account"])
            self.call_update_callback()
    
    def filter_activate(self, action):
        self.pfilter.run()
        self.update_widget()

    def update_widget(self):
        if self.database.connection == None:
            self.positions_list.update_rows([])
            return
        self.positions_list.update_rows(self.pfilter.get_ids(fields = ['id',
                                                                       'open_date_formated',
                                                                       'open_time_formated',
                                                                       'close_date_formated',
                                                                       'close_time_formated',
                                                                       'formated_duration',
                                                                       'ticket',
                                                                       'count',
                                                                       'direction_formated',
                                                                       'open_coast',
                                                                       'close_coast',
                                                                       'coast_range_formated',
                                                                       'gross_before',
                                                                       'gross_after',
                                                                       'pl_gross_range_formated',
                                                                       'net_before',
                                                                       'net_after',
                                                                       'pl_net_range_formated',
                                                                       'plnet_acc_formated'],
                                                             order_by = self.order_by))

    def sort_callback(self, column, order, parameters):
        self.order_by = parameters[0]
        if order == gtk.SORT_DESCENDING:
            self.order_by += ' desc'
        self.update_widget()
                                                                       
        
