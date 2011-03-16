#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_checkbutton import hiding_checkbutton
from datetime_widget import datetime_widget
import datetime

class from_to_datetime_widget(hiding_checkbutton):
    def __init__(self, name, vertical = True):
        if vertical:
            box = gtk.VBox()
        else:
            box = gtk.HBox()
        self.fromtime = datetime_widget(">=")
        self.totime = datetime_widget("<=")
        self.fromtime.checkbutton.connect("toggled", self.child_toggled)
        self.totime.checkbutton.connect("toggled", self.child_toggled)
        box.pack_start(self.fromtime.get_widget(), False)
        box.pack_start(self.totime.get_widget(), False)
        hiding_checkbutton.__init__(self, name, box)

    def child_toggled(self, tb):
        if (not self.fromtime.checkbutton.get_active()) and (not self.totime.checkbutton.get_active()):
            self.checkbutton.set_active(False)

    def get_datetime_from(self):
        if self.fromtime.checkbutton.get_active():
            return datetime.datetime.combine(self.fromtime.get_date(), self.fromtime.get_time() or datetime.time(0, 0, 0))
        else:
            return None

    def get_datetime_to(self):
        if self.totime.checkbutton.get_active():
            return datetime.datetime.combine(self.totime.get_date(), self.totime.get_time() or datetime.time(23, 59, 59))
        else:
            return None

    

if __name__ == "__main__":
    def clicked(bt, dt, tb):
        tb.set_text(u'{0} {1}'.format(dt.get_datetime_from() and dt.get_datetime_from().isoformat() or "", dt.get_datetime_to() and dt.get_datetime_to().isoformat() or ""))
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    box = gtk.HBox()
    a = from_to_datetime_widget("get datetime")
    box.pack_start(a.get_widget(), False)
    box.pack_start(from_to_datetime_widget("get other datetime", False).get_widget(), False)
    vb = gtk.VBox()
    vb.pack_start(box)
    tw = gtk.TextView()
    tb = tw.get_buffer()
    bt = gtk.Button("pushme")
    vb.pack_start(tw, False)
    vb.pack_start(bt, False)
    bt.connect("clicked", clicked, a, tb)
    w.add(vb)
    w.show_all()
    gtk.main()
        
