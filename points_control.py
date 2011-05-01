#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
import sqlite3
from common_methods import *
from combo_control import *
from number_range_control import number_control
from list_view_sort_control import *

class points_control:
    def __init__(self, database, builder):
        self.builder = builder
        self.database = database
        def shorter(name):
            return self.builder.get_object(name)
        w = shorter("points")
        w.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)
        self.instrument = combo_control(shorter("points_instrument"))
        self.instrument_class = combo_control(shorter("points_class"))
        self.point = shorter("points_point")
        self.step = shorter("points_step")
        for sp in [self.point, self.step]:
            sp.set_digits(6)
            sp.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1)
        self.add = shorter("points_add")
        self.delete = shorter("points_delete")
        self.add.connect("clicked", self.add_clicked)
        self.delete.connect("clicked", self.delete_clicked)
        tw = shorter("points_points")
        self.points_list = list_view_sort_control(tw, [(u'id', gtk.CellRendererSpin(), int),
                                                       (u'Класс', gtk.CellRendererText(), str),
                                                       (u'Инструмент', gtk.CellRendererText(), str),
                                                       (u'Пункт', gtk.CellRendererSpin(), float),
                                                       (u'Шаг', gtk.CellRendererSpin(), float)])
        tw.connect("cursor-changed", self.points_cursor_changed)
        shorter("points_class").connect("changed", self.class_changed)

    def add_clicked(self, bt):
        self.add_item()
        self.load_points_list()

    def delete_clicked(self, bt):
        self.delete_item()
        self.load_points_list()

    def points_cursor_changed(self, tw):
        self.set_item_values()

    def class_changed(self, combobox):
        self.load_instruments()

    @if_database
    def run(self):
        w = self.builder.get_object("points")
        self.load_classes()
        self.load_points_list()
        w.show_all()
        w.run()
        w.hide()

    @if_database
    def set_item_values(self):
        (mod, it) = self.builder.get_object("points_points").get_selection().get_selected()
        if it != None:
            self.instrument_class.set_value(mod.get_value(it, 1))
            self.instrument.set_value(mod.get_value(it, 2))
            self.point.set_value(mod.get_value(it, 3))
            self.step.set_value(mod.get_value(it, 4))

    @if_database
    def load_points_list(self):
        self.points_list.update_rows(self.database.get_points())

    @if_database
    def load_classes(self):
        self.instrument_class.update_widget(self.database.get_classes())

    @if_database
    def load_instruments(self):
        val = self.instrument_class.get_value()
        if val != None:
            self.instrument.update_widget(self.database.get_instruments_of_class(val))

    @if_database
    def delete_item(self):
        (mod, it) = self.builder.get_object("points_points").get_selection().get_selected()
        if it != None:
            self.database.delete_point(mod.get_value(it, 0))

    @if_database
    def add_item(self):
        if not is_null_or_empty(self.instrument.get_value()) and not is_null_or_empty(self.instrument_class.get_value()) and self.point.get_value() > 0 and self.step.get_value() > 0:
            try:
                self.database.add_point(self.instrument_class.get_value(), self.instrument.get_value(), self.point.get_value(), self.step.get_value())
            except sqlite3.IntegrityError:
                pass
            

            

