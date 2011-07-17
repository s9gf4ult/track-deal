#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
import sqlite3
from common_methods import *
from combo_select_control import combo_select_control
from number_range_control import number_control
from list_view_sort_control import *
from modifying_tab_control import modifying_tab_control

class points_control(modifying_tab_control):
    def __init__(self, parent):
        self._parent = parent
        def shorter(name):
            return self._parent.builder.get_object(name)
        w = shorter("points")
        w.set_transient_for(shorter('main_window'))
        w.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.instrument = combo_select_control(shorter("points_instrument"))
        self.money = combo_select_control(shorter("points_paper"))
        self.point = shorter("points_point")
        self.step = shorter("points_step")
        for sp in [self.point, self.step]:
            sp.set_digits(6)
            sp.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1)
        self.add = shorter("points_add")
        self.delete = shorter("points_delete")
        self.modify = shorter("points_modify")
        self.add.connect("clicked", self.add_clicked)
        self.delete.connect("clicked", self.delete_clicked)
        self.modify.connect("clicked", self.modify_clicked)
        tw = shorter("points_points")
        self.points_list = list_view_sort_control(tw, [[u'id', int],
                                                       (u'Валюта', gtk.CellRendererText(), str),
                                                       (u'Инструмент', gtk.CellRendererText(), str),
                                                       (u'Пункт', gtk.CellRendererSpin(), float),
                                                       (u'Шаг', gtk.CellRendererSpin(), float),
                                                       [u'money_id', int],
                                                       [u'paper_id', int]])
        tw.connect("cursor-changed", self.points_cursor_changed)

    def add_clicked(self, bt):
        self.add_item()

    def delete_clicked(self, bt):
        self.delete_item()

    def modify_clicked(self, bt):
        """\brief modify button click handler
        \param bt - gtk.Button()
        """
        self.modify_item()

    def points_cursor_changed(self, tw):
        """\brief points list 'cursor-changed' handler
        \param tw - gtk.TreeView()
        """
        self.set_item_values()

    def set_item_values(self, ):
        """\brief set values from selected item to the fields
        """
        row = self.points_list.get_selected_row()
        if row == None:
            return
        self.money.set_value(row[5])
        self.instrument.set_value(row[6])
        self.step.set_value(row[4])
        self.point.set_value(row[3])
        print("done")

    def delete_item(self, ):
        """\brief delete selected item from list and from the database
        """
        if not self._parent.connected():
            return
        row = self.points_list.get_selected_row()
        if row == None:
            return
        try:
            self._parent.model.remove_point(row[0])
        except sqlite3.IntegrityError:
            pass
        except Exception as e:
            show_and_print_error(e, self._parent.builder.get_object('points'))
        else:
            self.points_list.delete_selected()

    def add_item(self, ):
        """\brief add new item from the fields 
        """
        if not self._parent.connected():
            return
        try:
            poid = self._parent.model.create_point(self.instrument.get_value(),
                                                   self.money.get_value(),
                                                   self.point.get_value(),
                                                   self.step.get_value())
        except sqlite3.IntegrityError as e:
            show_and_print_error(e, self._parent.builder.get_object('points'))
            pass
        except Exception as e:
            show_and_print_error(e, self._parent.builder.get_object('points'))
        else:
            m = self._parent.model.get_money(self.money.get_value())
            p = self._parent.model.get_paper(self.instrument.get_value())
            self.points_list.add_row((poid, m['name'], p['name'], self.point.get_value(), self.step.get_value(), m['id'], p['id']))

    def modify_item(self, ):
        """\brief modify selected item with fields
        """
        if not self._parent.connected():
            return
        row = self.points_list.get_selected_row()
        if row == None:
            return
        try:
            self._parent.model.change_point(row[0],
                                            self.money.get_value(),
                                            self.instrument.get_value(),
                                            self.point.get_value(),
                                            self.step.get_value())
        except sqlite3.IntegrityError:
            pass
        except Exception as e:
            show_and_print_error(e, self._parent.builder.get_object('points'))
        else:
            m = self._parent.model.get_money(self.money.get_value())
            p = self._parent.model.get_paper(self.instrument.get_value())
            self.points_list.save_value_in_selected(1, m['name'])
            self.points_list.save_value_in_selected(2, p['name'])
            self.points_list.save_value_in_selected(3, self.point.get_value())
            self.points_list.save_value_in_selected(4, self.step.get_value())
            self.points_list.save_value_in_selected(5, m['id'])
            self.points_list.save_value_in_selected(6, p['id'])

    def update_widget(self, ):
        """\brief update checkboxes
        """
        if not self._parent.connected():
            return
        self.instrument.update_answers(map(lambda a: (a['id'], a['name']), self._parent.model.list_papers(['name'])))
        self.money.update_answers(map(lambda a: (a['id'], a['name']), self._parent.model.list_moneys(['name'])))
        points = self._parent.model.list_points_view(['money_name', 'paper_name'])
        self.points_list.update_rows(map(lambda a: (a['id'], a['money_name'], a['paper_name'], a['point'], a['step'], a['money_id'], a['paper_id']), points.fetchall()))

    def run(self):
        """\brief run dialog and return result of running
        \retval gtk.RESPONSE_ACCEPT - if 'save' prssed
        \retval gtk.RESPONSE_CANCEL - if 'cancel' pressed
        \note this is the blocking "show" method, uses "run"
        """
        if not self._parent.connected():
            return
        self.update_widget()
        w = self._parent.builder.get_object('points')
        try:
            self._parent.model.start_transacted_action('create some points')
            ret = w.run()
        except Exception as e:
            show_and_print_error(e, self._parent.builder.get_object('main_window'))
            self._parent.model.rollback()
            w.hide()
            return gtk.RESPONSE_CANCEL
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.model.commit_transacted_action()
            self._parent.model.recalculate_all_temporary()
            self._parent.call_update_callback()
        else:
            self._parent.model.rollback()
        w.hide()
        return ret
        
