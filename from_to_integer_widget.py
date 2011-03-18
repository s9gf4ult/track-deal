#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_checkbutton import hiding_checkbutton

class from_to_integer_widget(hiding_checkbutton):
    def __init__(self, name, from_adjustment, to_adjustment, vertical = True, expand = False, digits = 0, hide = True):
        self.from_entry = gtk.SpinButton(adjustment = from_adjustment, climb_rate = 0.1, digits = digits)
        self.to_entry = gtk.SpinButton(adjustment = to_adjustment, climb_rate = 0.1, digits = digits)
        if vertical:
            box = gtk.VBox()
        else:
            box = gtk.HBox()
        self.from_hcheck = hiding_checkbutton(">=", self.from_entry, hide = hide)
        self.from_hcheck.checkbutton.connect("toggled", self.child_toggled)
        self.to_hcheck = hiding_checkbutton("<=", self.to_entry, hide = hide)
        self.to_hcheck.checkbutton.connect("toggled", self.child_toggled)
        box.pack_start(self.from_hcheck.get_widget(), expand)
        box.pack_start(self.to_hcheck.get_widget(), expand)
        hiding_checkbutton.__init__(self, name, box, hide = hide)

    def child_toggled(self, tb):
        if (not self.from_hcheck.checkbutton.get_active()) and (not self.to_hcheck.checkbutton.get_active()):
            self.checkbutton.set_active(False)

    def get_from_integer(self):
        if self.checkbutton.get_active() and self.from_hcheck.checkbutton.get_active():
            return self.from_entry.get_value()
        else:
            return None

    def get_to_integer(self):
        if self.checkbutton.get_active() and self.to_hcheck.checkbutton.get_active():
            return self.to_entry.get_value()
        else:
            return None

if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    w.add(from_to_integer_widget("ijij", gtk.Adjustment(lower = 0, upper = 100, step_incr = 1), gtk.Adjustment(lower = 100, upper = 200, step_incr = 1)).get_widget())

    w.show_all()
    gtk.main()
                                 
