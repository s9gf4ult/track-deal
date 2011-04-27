#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
import datetime
import time
from hide_control import value_returner_control
import sys


class datetime_control(value_returner_control):
    react = True
    value = datetime.datetime.now()
    def __init__(self, calendar, time_control, checkbutton = None, year = None, month = None, day = None):
        self.calendar = calendar
        self.year = year
        self.month = month
        self.day = day
        self.time_control = time_control
        self.checkbutton = checkbutton
        for (wid, callb) in [(self.year, self.year_changed),
                             (self.month, self.month_changed),
                             (self.day, self.day_changed)]:
            if wid != None:
                wid.connect("value-changed", callb)
        for (wid, low, up) in [(self.year, 0, sys.float_info.max),
                               (self.month, 1, 12),
                               (self.day, 1, 31)]:
            if wid != None:
                wid.get_adjustment().set_all(lower = low, upper = up, step_increment = 1, page_increment = 5)
        if self.month != None:
            self.month.set_wrap(True)
        self.calendar.connect("day-selected", self.calendar_day_changed)
        self.calendar.connect("month-changed", self.calendar_month_changed)

    def year_changed(self, spin):
        self.value = self._value_from_dd()
        self._restore_from_value()
    
    def month_changed(self, spin):
        self.value = self._value_from_dd()
        self._restore_from_value()
    
    def day_changed(self, spin):
        try:
            x = self._value_from_dd()
            self.value = x
        except ValeError:
            pass
        else:
            self._restore_from_value()

    def _value_from_dd(self):
        return datetime.datetime(self.year.get_value_as_int(), self.month.get_value_as_int(), self.day.get_value_as_int())

    def _value_from_calendar(self):
        dd = self.calendar.get_date()
        return datetime.datetime(dd[0], dd[1] + 1, dd[2])
    
    def calendar_day_changed(self, calendar):
        self.set_date(self._value_from_calendar())

    def calendar_month_changed(self, calendar):
        self.set_date(self._value_from_calendar())

    def _restore_from_value(self):
        if not self.react:
            return
        self.react = False
        try:
            self.calendar.select_month(self.value.month - 1, self.value.year)
            self.calendar.select_day(self.value.day)
            for (wid, val) in [(self.year, self.value.year),
                               (self.month, self.value.month),
                               (self.day, self.value.day)]:
                if wid != None:
                    wid.set_value(val)
            self.time_control.set_time(self.value.time())
        finally:
            self.react = True
        

    def get_date(self):
        return self.return_value(self.value.date())

    def get_time(self):
        return self.return_value(self.value.time())

    def get_datetime(self):
        return self.return_value(self.value)

    def set_current_time(self):
        self.set_time(datetime.datetime.now().time())

    def set_time(self, time):
        self.value = datetime.datetime.combine(self.value.date(), time)
        self._restore_from_value()

    def set_current_date(self):
        self.set_date(datetime.datetime.now().date())

    def set_current_datetime(self):
        self.value = datetime.datetime.now()
        self._restore_from_value()

    def set_datetime(self, dd):
        self.value = dd
        self._restore_from_value()

    def set_date(self, date):
        self.value = datetime.datetime.combine(date, self.value.time())
        self._restore_from_value()

if __name__ == "__main__":
    from time_control import *
    w = gtk.Dialog()
    p = w.get_content_area()
    cdt = gtk.CheckButton("all")
    cal = gtk.Calendar()
    ct = gtk.CheckButton("time")
    h = gtk.SpinButton()
    m = gtk.SpinButton()
    s = gtk.SpinButton()
    tcon = time_control(h, m, s, ct)
    dtcon = datetime_control(cal, tcon, cdt)
    b = gtk.Button("push")
    l = gtk.Label()
    def clicked(bt):
        l.set_text("{0} - {1}".format(dtcon.get_date(), dtcon.get_time()))
    b.connect("clicked", clicked)
    def clickedb(bt):
        dtcon.set_current_datetime()
    bb = gtk.Button("set curront")
    bb.connect("clicked", clickedb)
    for wi in [cdt, cal, ct, h, m, s, b, l, bb]:
        p.pack_start(wi)
    w.show_all()
    w.run()
