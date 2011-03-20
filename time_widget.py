#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import datetime, time

class time_widget:
    def __init__(self):
        self.hbox=gtk.HBox()
        self.hour = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 23, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.min = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 59, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.sec = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 59, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.hbox.pack_start(self.hour, False)
        self.hbox.pack_start(gtk.Label(":"), False)
        self.hbox.pack_start(self.min, False)
        self.hbox.pack_start(gtk.Label(":"), False)
        self.hbox.pack_start(self.sec, False)

    def get_hour(self):
        return self.hour.get_value_as_int()

    def get_min(self):
        return self.min.get_value_as_int()

    def get_sec(self):
        return self.sec.get_value_as_int()

    def set_current_time(self):
        dd = datetime.datetime.fromtimestamp(time.time())
        self.hour.set_value(dd.hour)
        self.min.set_value(dd.minute)
        self.sec.set_value(dd.second)

    def get_widget(self):
        return self.hbox
