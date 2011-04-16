#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import hide_control
from number_range_control import *

class hiding_number_range_control(number_range_control):
    def __init__(self, lower_spin, upper_spin, global_box = None, global_chbt = None, lower_chbt = None, upper_chbt = None, step_incr = 1, digits = 0):
        self.hiders = []
        for (bt, box) in [(global_chbt, global_box),
                          (lower_chbt, lower_spin),
                          (upper_chbt, upper_spin)]:
            if bt != None and box != None:
                self.hiders.append(hide_control(bt, [box]))
        subhide = filter(lambda a: a != None, [lower_chbt, upper_bhbt])
        if len(subhide) > 0 and global_chbt != None:
            self.subhiders = all_checked_control(global_chbt, subhide)
        lower = number_control(lower_spin, lower_chbt, step_incr, digits)
        upper = number_control(upper_spin, upper_chbt, step_incr, digits)
        number_range_control.__init__(self, lower, upper, global_chbt)
                                   
