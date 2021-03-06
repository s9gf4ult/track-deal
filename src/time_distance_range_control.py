#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import value_returner_control
import sys
import math
import gtk

class time_distance_control(value_returner_control):
    """
    \brief control for editing time value as secons count
    """
    def __init__(self, day_spin = None, hour_spin = None, min_spin = None, sec_spin = None, checkbutton = None):
        """
        \param day_spin - gtk.SpinButton instance describing day
        \param hour_spin - gtk.SpinButton instance describing hour
        \param min_spin - gtk.SpinButton instance describing minute
        \param sec_spin - gtk.SpinButton instance describing seconds
        \param checkbutton - gtk.ToggleButton instance to control return value or do not
        """
        self.checkbutton = checkbutton
        self.day = day_spin
        self.hour = hour_spin
        self.min = min_spin
        self.sec = sec_spin
        for spin in [self.day, self.hour, self.min, self.sec]:
            if spin != None:
                spin.set_digits(0)

        for spin in [self.min, self.sec]:
            if spin != None:
                spin.get_adjustment().set_all(lower = 0, upper = 59, step_increment = 1, page_increment = 5)
        if self.day != None:
            self.day.get_adjustment().set_all(lower = 0, upper = sys.float_info.max, step_increment = 1, page_increment = 5)
        if self.hour != None:
            self.hour.get_adjustment().set_all(lower = 0, upper = 23, step_increment = 1, page_increment = 5)

    def get_hour_value(self):
        return (self.hour != None and self.hour.get_value() or 0)

    def get_day_value(self):
        return (self.day != None and self.day.get_value() or 0)

    def get_min_value(self):
        return (self.min != None and self.min.get_value() or 0)

    def get_sec_value(self):
        return (self.sec != None and self.sec.get_value() or 0)

    def get_seconds(self):
        return self.return_value(60 * self.get_min_value() + 3600 * self.get_hour_value() + 3600 * 24 * self.get_day_value() + self.get_sec_value())
    
    def set_seconds(self, seconds):
        for (spin, mulator) in [(self.day, 3600 * 24),
                                (self.hour, 3600),
                                (self.min, 60),
                                (self.sec, 1)]:
            if spin != None:
                spin.set_value(math.trunc(seconds / mulator))
                seconds = seconds % mulator

class time_distance_range_control(value_returner_control):
    """
    \brief control to work with two time_distance_control instances to get the distance between them
    """
    def __init__(self, lower_control, upper_control, checkbutton = None):
        """
        \param lower_control - \ref time_distance_control instance - the lower limit of range
        \param upper_control - \ref time_distance_control instance - the uppper limit of range
        \param checkbutton - gtk.ToggleButton instance to control return value or do not
        """
        self.lower = lower_control
        self.upper = upper_control
        self.checkbutton = checkbutton

    def get_lower_seconds(self):
        return self.return_value(self.lower.get_seconds())

    def get_upper_seconds(self):
        return self.return_value(self.upper.get_seconds())

    def set_seconds(self, lower_sec, upper_sec):
        self.lower.set_seconds(lower_sec)
        self.upper.set_seconds(upper_sec)


if __name__ == "__main__":
    dial = gtk.Dialog()
    p = dial.get_content_area()
    d = gtk.SpinButton()
    h = gtk.SpinButton()
    m = gtk.SpinButton()
    for w in [d, h, m]:
        p.pack_start(w, False)
    con = time_distance_control(d, h, m)
    con.set_seconds(3600 * 24 * 1 + 3600 * 1 + 1 * 60)
    dial.show_all()
    dial.run()
    print(con.get_seconds())
    
