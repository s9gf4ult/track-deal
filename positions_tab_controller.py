#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import *
import gtk
from common_methods import *

class positions_tab_controller(modifying_tab_control):
    order_by = None
    def __init__(self, global_data, database, builder, pfilter, update_callback):
        self.database = database
        self.builder = builder
        self.pfilter = pfilter
        self.global_data = global_data
        self.update_callback = update_callback
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)
        self.positions_list = list_view_sort_control(self.builder.get_object("positions_view"),
                                                     [(u'Дата Откр.', gtk.CellRendererText(), str, u'open_datetime'),
                                                      (u'время Откр.', gtk.CellRendererText(), str, u'open_time'),
                                                      (u'Дата Закр.', gtk.CellRendererText(), str, u'close_datetime'),
                                                      (u'Время Закр.', gtk.CellRendererText(), str, u'close_time'),
                                                      (u'В позиции', gtk.CellRendererText(), str, u'duration'),
                                                      (u'Тикер', gtk.CellRendererText(), str, u'ticket'),
                                                      (u'Кол-во', gtk.CellRendererSpin(), int, u'count'),
                                                      (u'Тип', gtk.CellRendererText(), str, u'direction'),
                                                      (u'Цена Откр.', gtk.CellRendererSpin(), float, u'open_coast'),
                                                      (u'Цена Закр.', gtk.CellRendererSpin(), float, u'close_coast'),
                                                      (u'Ход', gtk.CellRendererSpin(), float, u'coast_range')],
                                                     
                                                     self_sorting = False,
                                                     sort_callback = self.sort_callback)
                                                     
        shorter("positions_make", "activate", self.make_positions_activate)
        shorter("call_positions_filter", "activate", self.filter_activate)

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
            return
        self.positions_list.update_rows(self.pfilter.get_ids(fields = ['open_date_formated',
                                                                       'open_time_formated',
                                                                       'close_date_formated',
                                                                       'close_time_formated',
                                                                       'formated_duration',
                                                                       'ticket',
                                                                       'count',
                                                                       'direction_formated',
                                                                       'open_coast',
                                                                       'close_coast',
                                                                       'coast_range'],
                                                             order_by = self.order_by))

    def sort_callback(self, column, order, parameters):
        self.order_by = parameters[0]
        if order == gtk.SORT_DESCENDING:
            self.order_by += ' desc'
        self.update_widget()
                                                                       
        
