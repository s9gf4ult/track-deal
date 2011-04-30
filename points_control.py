#!/bin/env python
# -*- codign: utf-8 -*-
import gtk
import sys
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
