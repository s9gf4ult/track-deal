#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hiding_checkbutton import hiding_checkbutton
import datetime
from time_widget import time_widget

class datetime_widget(hiding_checkbutton):
    def __init__(self, name, hide = True):
        self.calendar = gtk.Calendar()
        self.time_widget = time_widget()
        self.time = hiding_checkbutton(u'Учитывать время', self.time_widget.get_widget())
        v = gtk.VBox()
        v.pack_start(self.calendar, False, True)
        v.pack_start(self.time.get_widget(), False)
        hiding_checkbutton.__init__(self, name, v, hide = hide)

    def get_date(self):
        if self.checkbutton.get_active():
            date = self.calendar.get_date()
            return datetime.date(date[0], date[1] + 1, date[2])
        else:
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
