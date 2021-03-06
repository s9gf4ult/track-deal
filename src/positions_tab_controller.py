#!/bin/env python
# -*- coding: utf-8 -*-

from list_view_sort_control import *
import gtk
from common_methods import *
import gtk_view
import sqlite3
from od_exceptions import od_exception_config_key_error

class positions_tab_controller(object):
    
    def __init__(self, parent):
        """
        \param parent \ref gtk_view.gtk_view instance as parent
        """
        self.order_by = []
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        def shorter(name, action, *method):
            self._parent.window.builder.get_object(name).connect(action, *method)
        self.positions_list = list_view_sort_control(self._parent.window.builder.get_object("positions_view"),
                                                     [[u'id', int],
                                                      (u'Дата Откр.', gtk.CellRendererText(), str, u'open_datetime'),
                                                      (u'время Откр.', gtk.CellRendererText(), str, u'open_time'),
                                                      (u'Дата Закр.', gtk.CellRendererText(), str, u'close_datetime'),
                                                      (u'Время Закр.', gtk.CellRendererText(), str, u'close_time'),
                                                      (u'В позиции', gtk.CellRendererText(), str, u'duration'),
                                                      (u'Инструмент', gtk.CellRendererText(), str, u'paper_name'),
                                                      (u'Кол-во', gtk.CellRendererText(), str, u'count'),
                                                      (u'Тип', gtk.CellRendererText(), str, u'direction'),
                                                      (u'Цена Откр.', gtk.CellRendererText(), str, u'open_price'),
                                                      (u'Цена Закр.', gtk.CellRendererText(), str, u'close_price'),
                                                      (u'Ход', gtk.CellRendererText(), str, u'steps_range'),
                                                      (u'Gross Bfr.', gtk.CellRendererText(), str, u'gross_before'),
                                                      (u'Gross Aftr.', gtk.CellRendererText(), str, u'gross_after'),
                                                      (u'P/L Gross', gtk.CellRendererText(), str, u'pl_gross_abs'),
                                                      (u'Net Bfr.', gtk.CellRendererText(), str, u'net_before'),
                                                      (u'Net Aftr.', gtk.CellRendererText(), str, u'net_after'),
                                                      (u'P/L Net', gtk.CellRendererText(), str, u'pl_net_abs'),
                                                      (u'% Изменения', gtk.CellRendererText(), str, u'percent_range_abs')],
                                                     self_sorting = False,
                                                     sort_callback = self.sort_callback)
        self._parent.window.builder.get_object("positions_view").get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        shorter("positions_make", "activate", self.make_positions_activate)
        shorter("call_positions_filter", "activate", self.filter_activate)
        shorter("delete_positions", "activate", self.delete_positions_activate)
        shorter("add_position", "activate", self.add_position_activate)
        shorter("update_positions", "activate", self.update_positions_activate)

    def update_positions_activate(self, action):
        self.update_positions()

    def update_positions(self):
        if not self._parent.connected():
            return
        self._parent.model.recalculate_all_temporary()
        self.update()

    def add_position_activate(self, action):
        self.add_position()

    def add_position(self):
        if not self._parent.connected():
            return
        self._parent.position_adder.update_widget()
        ret = self._parent.position_adder.run()
        if ret == gtk.RESPONSE_ACCEPT:
            try:
                data = self._parent.position_adder.get_data()
                self._parent.model.tacreate_position_from_data(data['account_id'],
                                                               data)
            except Exception as e:
                show_and_print_error(e, self._parent.window.builder.get_object("main_window"))
            else:
                self._parent.call_update_callback()

    def delete_positions_activate(self, action):
        self.delete_positions()

    def delete_positions(self):
        if not self._parent.connected():
            return
        rows = self.positions_list.get_selected_rows()
        if not is_null_or_empty(rows):
            try:
                self._parent.model.taremove_position(map(lambda a: a[0], rows))
            except sqlite3.IntegrityError:
                pass
            else:
                self._parent.call_update_callback()
            
    def make_positions_activate(self, action):
        self.make_positions()

    def make_positions(self):
        if not self._parent.connected():
            return
        cacc = self._parent.model.get_current_account()
        if cacc <> None:
            self._parent.model.tamake_positions_for_whole_account(cacc["id"])
            self._parent.model.recalculate_all_temporary()
            self._parent.call_update_callback()
    
    def filter_activate(self, action):
        self._parent.positions_filter.update_filter()
        self._parent.positions_filter.run()
        self.update()

    def update(self):
        """\brief updte list with positions
        """
        try:
            self.positions_list.set_odd_color(self._parent.settings.get_key('interface.odd_color'))
            self.positions_list.set_even_color(self._parent.settings.get_key('interface.even_color'))
        except od_exception_config_key_error:
            pass
        if not self._parent.connected():
            self.positions_list.update_rows([])
            return
        self._parent.positions_filter.update_filter()
        self.positions_list.update_rows(map(lambda a: (a['position_id'],
                                                       a['open_date_formated'],
                                                       a['open_time_formated'],
                                                       a['close_date_formated'],
                                                       a['close_time_formated'],
                                                       a['duration_formated'],
                                                       a['paper_name'],
                                                       a['count'],
                                                       a['direction_formated'],
                                                       a['open_price_formated'],
                                                       a['close_price_formated'],
                                                       a['steps_range_abs_formated'],
                                                       format_number(a['gross_before']),
                                                       format_number(a['gross_after']),
                                                       a['pl_gross_abs_formated'],
                                                       format_number(a['net_before']),
                                                       format_number(a['net_after']),
                                                       a['pl_net_abs_formated'],
                                                       a['percent_range_abs_formated']), self._parent.positions_filter.get_data(self.order_by)))
        

    def sort_callback(self, column, order, parameters):
        self.order_by = parameters[0]
        if order == gtk.SORT_DESCENDING:
            self.order_by += ' desc'
        self.order_by = [self.order_by]
        self.update()        
