#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
import datetime
import time
from hide_control import value_returner_control

class datetime_control(value_returner_control):
    def __init__(self, calendar, time_control, checkbutton = None):
        self.calendar = calendar
        self.time_control = time_control
        self.checkbutton = checkbutton

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

    def set_current_date(self):
        dd = datetime.datetime.fromtimestamp(time.time())
        self.calendar.select_month((dd.month - 1), dd.year)
        self.calendar.select_day(dd.day)

    def set_current_datetime(self):
        self.set_current_time()
        self.set_current_date()

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
