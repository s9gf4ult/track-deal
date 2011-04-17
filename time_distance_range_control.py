#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import value_returner_control
import sys
import math

class time_distance_control(value_returner_control):
    def __init__(self, day_spin, hour_spin, min_spin, checkbutton = None):
        self.checkbutton = checkbutton
        self.day = day_spin
        self.hour = hour_spin
        self.min = min_spin
        for spin in [self.day, self.hour]:
            if spin != None:
                spin.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1, page_increment = 5)
                spin.set_digits(0)

        if self.min != None:
            self.min.get_adjustment().get_all(lower = 0, upper = sys.float_info.max, step_increment = 1, page_increment = 5)
            self.min.set_digits(2)

    def get_hour_value(self):
        return (self.hour != None and self.hour.get_value() or 0)

    def get_day_value(self):
        return (self.day != None and self.day.get_value() or 0)

    def get_min_value(self):
        return (self.min != None and self.min.get_value() or 0)

    def get_seconds(self):
        return self.return_value(60 * self.get_min_value() + 3600 * self.get_hour_value() + 3600 * 24 * self.get_day_value())
    
    def set_seconds(self, seconds):
        for (spin, mulator) in [(self.day, 3600 * 24),
                                (self.hour, 3600)]:
            if spin != None:
                spin.set_value(math.trunc(seconds / mulator))
                seconds = seconds % mulator
        if self.min != None:
            self.min.set_value(seconds / 60)
                
