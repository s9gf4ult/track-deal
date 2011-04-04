#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import value_returner_control

class number_control(value_returner_control):
    def __init__(self, spin_button, checkbutton = None, step_incr = 1, digits = 0):
        self.checkbutton = checkbutton
        self.spin_button = spin_button
        self.spin_button.set_digits(digits)
        self.spin_button.get_adjustment().set_step_increment(step_incr)

    def set_lower_limit(self, limit):
        if limit:
            self.spin_button.get_adjustment().set_lower(limit)

    def set_upper_limit(self, limit):
        if limit:
            self.spin_button.get_adjustment().set_upper(float(limit))

    def get_value(self):
        return self.return_value(self.spin_button.get_value())

class number_range_control(value_returner_control):
    def __init__(self, low_control, high_control, checkbutton = None):
        self.checkbutton = checkbutton
        self.low_control = low_control
        self.high_control = high_control

    def set_lower_limit(self, limit):
        self.low_control.set_lower_limit(limit)
        self.high_control.set_lower_limit(limit)

    def set_upper_limit(self, limit):
        self.low_control.set_upper_limit(limit)
        self.high_control.set_upper_limit(limit)

    def get_lower_value(self):
        return self.return_value(self.low_control.get_value())

    def get_upper_value(self):
        return self.return_value(self.high_control.get_value())
        
if __name__ == "__main__":
    w = gtk.Dialog(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    p = w.get_content_area()
    a = gtk.CheckButton("One")
    b = gtk.CheckButton("Two")
    c = gtk.CheckButton("Both")
    aa = gtk.SpinButton()
    bb = gtk.SpinButton()
    x = number_control(aa, a)
    y = number_control(bb, b)
    n = number_range_control(x, y, c)
    n.set_lower_limit(0)
    n.set_upper_limit(100)
    for wi in [c, a, aa, b, bb]:
        p.pack_start(wi, False)
    e = gtk.Entry()
    b = gtk.Button("push")
    def clicked(bt):
        e.set_text("{0} - {1}".format(n.get_lower_value(), n.get_upper_value()))
    b.connect("clicked", clicked)
    p.pack_start(e, False)
    p.pack_start(b)
    w.show_all()
    w.run()
