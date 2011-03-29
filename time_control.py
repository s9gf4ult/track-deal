#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import datetime, time
import value_returner_control from hide_control

class time_control(value_returner_control):
    def __init__(self, hour, min, sec, checkbutton = None):
        self.hour = hour
        self.min = min
        self.sec = sec
        self.checkbutton = checkbutton
        self.hour.set_range(0, 23)
        self.hour.set_increments(1, 5)
        self.hour.set_digits(0)
        for w in [self.min, self.sec]:
            w.set_range(0, 59)
            w.set_digits(0)
            w.set_increments(1, 10)
        

    def get_hour(self):
        return self.hour.get_value_as_int()

    def get_min(self):
        return self.min.get_value_as_int()

    def get_sec(self):
        return self.sec.get_value_as_int()

    def get_time(self):
        return self.return_value(datetime.time(self.get_hour(), self.get_min(), self.get_sec()))

    def set_current_time(self):
        dd = datetime.datetime.fromtimestamp(time.time())
        self.hour.set_value(dd.hour)
        self.min.set_value(dd.minute)
        self.sec.set_value(dd.second)

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    h = gtk.SpinButton()
    m = gtk.SpinButton()
    s = gtk.SpinButton()
    cb = gtk.CheckButton()
    con = time_control(h, m, s, cb)
    con.set_current_time()
    b = gtk.Button("get_time")
    l = gtk.Label()
    def clicked(bt):
        l.set_text("{0}".format(con.get_time()))
    b.connect("clicked", clicked)
    for wi in [cb, h, m, s, b, l]:
        p.pack_start(wi)
    w.show_all()
    w.run()
