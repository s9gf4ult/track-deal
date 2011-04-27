#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
import datetime
import time
from hide_control import value_returner_control

class datetime_control(value_returner_control):
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
        self.calendar.connect("day-selected", self.calendar_day_changed)
        self.calendar.connect("month-changed", self.calendar_month_changed)

    def year_changed(self, spin):
        pass

    def month_changed(self, spin):
        pass

    def day_changed(self, spin):
        pass

    def calendar_day_changed(self, calendar):
        pass

    def calendar_month_changed(self, calendar):
        pass
            

    def get_date(self):
        date = self.calendar.get_date()
        val = datetime.date(date[0], date[1] + 1, date[2])
        return self.return_value(val)

    def get_time(self):
        return self.return_value(self.time_control.get_time())

    def get_datetime(self):
        date = self.get_date()
        time = self.get_time()
        if date and time:
            return datetime.datetime.combine(date, time)
        return None

    def set_current_time(self):
        self.time_control.set_current_time()

    def set_time(self, time):
        self.time_control.set_time(time)

    def set_current_date(self):
        dd = datetime.datetime.fromtimestamp(time.time())
        self.set_date(dd)

    def set_date(self, date):
        self.calendar.select_month((date.month - 1), date.year)
        self.calendar.select_day(date.day)

    def set_current_datetime(self):
        self.set_current_time()
        self.set_current_date()

    def set_datetime(self, dd):
        self.set_date(dd.date())
        self.set_time(dd.time())

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
