#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hiding_checkbutton import hiding_checkbutton
import datetime

class datetime_widget(hiding_checkbutton):
    def __init__(self, name, hide = True):
        self.hour = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 23, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.min = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 59, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.sec = gtk.SpinButton(gtk.Adjustment(lower = 0, upper = 59, step_incr = 1), climb_rate = 0.1, digits = 0)
        self.calendar = gtk.Calendar()
        time = gtk.HBox()
        time.pack_start(self.hour, False)
        time.pack_start(gtk.Label(":"), False)
        time.pack_start(self.min, False)
        time.pack_start(gtk.Label(":"), False)
        time.pack_start(self.sec, False)
        self.time = hiding_checkbutton(u'Учитывать время', time)
        v = gtk.VBox()
        v.pack_start(self.calendar, False, True)
        v.pack_start(self.time.get_widget(), False)
        hiding_checkbutton.__init__(self, name, v, hide = hide)

    def get_date(self):
        if self.checkbutton.get_active():
            return datetime.date(*self.calendar.get_date())
        else:
            return None

    def get_time(self):
        if self.checkbutton.get_active() and self.time.checkbutton.get_active():
            return datetime.time(self.hour.get_value_as_int(), self.min.get_value_as_int(), self.sec.get_value_as_int())
        else:
            return None

if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    w.add(datetime_widget(u'datetime').get_widget())
    w.show_all()
    gtk.main()
