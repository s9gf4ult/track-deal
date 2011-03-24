#!/bin/env python
# -*- coding: utf-8 -*-

class number_range_control:
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
