#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class number_control:
    def __init__(self, spin_button, checkbutton = None, step_incr = 1):
        self.checkbutton = checkbutton
        self.spin_button = spin_button
        self.spin_button.get_adjustment().set_step_increment(step_incr)

    def set_lower_limit(self, limit):
        self.spin_button.get_adjustment().set_lower(limit)

    def set_upper_limit(self, limit):
        self.spin_button.get_adjustment().set_upper(limit)

    def get_value(self):
        val = self.spin_button.get_value()
        if self.checkbutton != None:
            if  self.checkbutton.get_active():
                return val
        else:
            return val
        return None

class number_range_control:
    def __init__(self, checkbutton, low_control, high_control):
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
        if self.checkbutton.get_active():
            return self.low_control.get_value()
        return None

    def get_upper_value(self):
        if self.checkbutton.get_active():
            return self.high_control.get_value()
        return None
        
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
    n = number_range_control(c, x, y)
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
