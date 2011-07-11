#!/bin/env python
# -*- coding: utf-8 -*-

from list_view_sort_control import *
import gtk
from common_methods import *
import gtk_view

class positions_tab_controller(object):
    order_by = ["position_id"]
    def __init__(self, parent):
        """
        \param parent \ref gtk_view.gtk_view instance as parent
        """
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        def shorter(name, action, *method):
            self._parent.builder.get_object(name).connect(action, *method)
        self.positions_list = list_view_sort_control(self._parent.builder.get_object("positions_view"),
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
        self._parent.builder.get_object("positions_view").get_selection().set_mode(gtk.SELECTION_MULTIPLE)
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
            except e:
                show_and_print_error(e, self._parent.builder.get_object("main_window"))
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
                self._parent.taremove_position(map(lambda a: a[0], rows))
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
            self._parent.call_update_callback()
    
    def filter_activate(self, action):
        self._parent.positions_filter.run()
        self.update()

    def update(self):
        """\brief updte list with positions
        \todo implement
        """
        if not self._parent.connected():
            self.positions_list.update_rows([])
            return

    def sort_callback(self, column, order, parameters):
        self.order_by = parameters[0]
        if order == gtk.SORT_DESCENDING:
            self.order_by += ' desc'
        self.order_by = [self.order_by]
        self.update()
                                                                       
        
