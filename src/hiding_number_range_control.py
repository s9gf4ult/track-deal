#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import *
from number_range_control import *

class hiding_number_range_control(number_range_control):
    def __init__(self, lower_spin, upper_spin, global_box = None, global_chbt = None, lower_chbt = None, upper_chbt = None, step_incr = 1, digits = 0):
        """
        \param lower_spin - gtk.SpinButton instance to display lower limit of range
        \param upper_spin - gtk.SpinButton instance to display upper limit of range
        \param global_box - gtk.Container with all widgets packed in to show or hide all the range-widget
        \param global_chbt - gtk.ToggleButton to control global_box show state
        \param lower_chbt - gtk.Container to control show state of lower range widget
        \param upper_chbt - gtk.Container to control show state of upper range widget
        \param step_incr - number, pass to \ref number_range_control.number_range_control
        \param digits - int, the same
        """
        self.hiders = []
        for (bt, box) in [(global_chbt, global_box),
                          (lower_chbt, lower_spin),
                          (upper_chbt, upper_spin)]:
            if bt != None and box != None:
                self.hiders.append(hide_control(bt, [box]))
        subhide = filter(lambda a: a != None, [lower_chbt, upper_chbt])
        if len(subhide) > 0 and global_chbt != None:
            self.subhiders = all_checked_control(global_chbt, subhide)
        lower = number_control(lower_spin, lower_chbt, step_incr, digits)
        upper = number_control(upper_spin, upper_chbt, step_incr, digits)
        number_range_control.__init__(self, lower, upper, global_chbt)
                                   
