#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
import datetime

class datetime_control:
    def __init__(self, calendar, time_control, checkbutton = None):
        self.calendar = calendar
        self.time_control = time_control
        self.checkbutton = checkbutton

    def get_date(self):
        date = self.calendar.get_date()
        val = datetime.date(date[0], date[1] + 1, date[2])
        if self.checkbutton != None:
            if self.checkbutton.get_active():
                return val
        else:
            return val
        return None

    def get_time(self):
        if self.checkbutton.get_active() and self.time.checkbutton.get_active():
            return datetime.time(self.time_widget.get_hour(), self.time_widget.get_min(), self.time_widget.get_sec())
        else:
            return None

if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    w.add(datetime_widget(u'datetime').get_widget())
    w.show_all()
    gtk.main()
