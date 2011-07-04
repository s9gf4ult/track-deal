#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import value_returner_control

class number_control(value_returner_control):
    """
    \brief simple wrapper for SpinButton
    """
    def __init__(self, spin_button, checkbutton = None, step_incr = 1, digits = 0):
        """
        \param spin_button
        \param checkbutton gtk.ToggleButton instance
        \param step_incr - int, step_incr from gtk.SpinButton
        \param digits - int, count of digits after the comma
        """
        self.checkbutton = checkbutton
        self.spin_button = spin_button
        self.spin_button.set_digits(digits)
        self.spin_button.get_adjustment().set_step_increment(step_incr)

    def set_lower_limit(self, limit):
        """
        \param limit - number, minimum for gtk.Adjustment
        """
        if limit:
            self.spin_button.get_adjustment().set_lower(limit)

    def set_upper_limit(self, limit):
        """
        \param limit - number, max for gtk.Adjustment
        """
        if limit:
            self.spin_button.get_adjustment().set_upper(float(limit))

    def get_value(self):
        """
        \retval None if checkbutton is not active
        \retval number - the value
        """
        return self.return_value(self.spin_button.get_value())

    def set_value(self, val):
        self.spin_button.set_value(val)

class number_range_control(value_returner_control):
    """
    \brief controls two \ref number_control instances to obtain the range of numbers
    """
    def __init__(self, low_control, high_control, checkbutton = None):
        """
        \param low_control - \ref number_control instance, low limit of the range
        \param high_control - \ref number_control instance, high limit of the range
        \param checkbutton - gtk.ToggleButton instance
        """
        self.checkbutton = checkbutton
        self.low_control = low_control
        self.high_control = high_control

    def set_lower_limit(self, limit):
        """\brief set lower limit for both number controls
        \param limit - number
        """
        self.low_control.set_lower_limit(limit)
        self.high_control.set_lower_limit(limit)

    def set_upper_limit(self, limit):
        """\brief set upper limit for both number controls
        \param limit - number
        """
        self.low_control.set_upper_limit(limit)
        self.high_control.set_upper_limit(limit)

    def get_lower_value(self):
        """
        \retval None if checkbutton is not active
        \retval number - lower value of the range
        """
        return self.return_value(self.low_control.get_value())

    def get_upper_value(self):
        """
        \retval None if checkbutton is not active
        \retval number - upper value of the range
        """
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
