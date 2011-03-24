#!/bin/env python
# -*- coding: utf-8 -*-

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
            self.checkbutton.get_active():
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
        
