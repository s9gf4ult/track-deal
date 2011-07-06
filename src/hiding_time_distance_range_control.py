#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import *
from time_distance_range_control import *
from common_methods import *

class hiding_time_distance_range_control(time_distance_range_control):
    """
    \brief wrapper for \ref time_distance_range_control.time_distance_range_control with "hide" behaviour implemented in \ref hide_control.hide_control
    """
    def __init__(self, lower, upper, box = [], checkbutton = None):
        """
        \param lower - hash table with keys:\n
        \c chbt - value is gtk.ToggleButton instance for \ref time_distance_range_control.time_distance_range_control constructor\n
        \c box - value is gtk.Container instance is the parameter for \ref hide_control.hide_control as widget to hide\n
        \c hour - value is gtk.SpinButton instance for \ref time_distance_range_control.time_distance_range_control constructor, is a hour\n
        \c min - value is gtk.SpinButton same as above but for minutes\n
        \c sec - same as above but for seconds
        \param upper - hash table with same keys as \c lower parameter but for upper limit of time range
        \param box - list of gtk.Container instances to "hide" with control \c checkbutton parameter
        \param checkbutton - gtk.CheckButton to hide and to control returned value
        """
        self.hiders = []
        for (chbt, boxes) in [(checkbutton, box),
                              (gethash(lower, "chbt"), [gethash(lower, "box")]),
                              (gethash(upper, "chbt"), [gethash(upper, "box")])]:
            rbx = filter(lambda a: a != None, boxes)
            if chbt != None and len(rbx) > 0:
                self.hiders.append(hide_control(chbt, rbx))
        subh = filter(lambda a: a != None, [gethash(lower, "chbt"), gethash(upper, "chbt")])
        if len(subh) > 0 and checkbutton != None:
            self.subhider = all_checked_control(checkbutton, subh)
        ctrls = map(lambda h: time_distance_control(day_spin = gethash(h, "day"), hour_spin = gethash(h, "hour"), min_spin = gethash(h, "min"), sec_spin = gethash(h, "sec"), checkbutton = gethash(h, "chbt")),
                    [lower, upper])
        time_distance_range_control.__init__(self, *(ctrls + [checkbutton]) )
