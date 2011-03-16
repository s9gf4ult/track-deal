#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_checkbutton import hiding_checkbutton
from datetime_widget import datetime_widget

class from_to_datetime_widtet(hiding_checkbutton):
    def __init__(self, name, vertical = True):
        if vertical:
            box = gtk.VBox()
        else:
            box = gtk.HBox()
        self.fromtime = datetime_widget(">=")
        self.totime = datetime_widget("<=")
        box.pack_start(self.fromtime.get_widget(), False)
        box.pack_start(self.totime.get_widget(), False)
        hiding_checkbutton.__init__(self, name, box)


if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    box = gtk.HBox()
    box.pack_start(from_to_datetime_widtet("get datetime").get_widget(), False)
    box.pack_start(from_to_datetime_widtet("get other datetime", False).get_widget(), False)
    w.add(box)
    w.show_all()
    gtk.main()
        
