#!/bin/env python
# -*- coding: utf-8 -*-

from time_control import time_control
from datetime_control import datetime_control
from datetime_range_control import datetime_range_control
from hide_control import *
from common_methods import *

class hiding_datetime_range_control(datetime_range_control):
    """
    \brief control to get datetime range.
    the same as \ref datetime_range_control but automatically creates \ref hide_control.hide_control and \ref hide_control.all_checked_control for the checkbuttons inside widget.
    """
    def __init__(self, lower, upper, box = [], checkbutton = None):
        """
        \param lower - hash table to construct controls over lower datetime widgets with keys:\n
        \c chbt - gtk.ToggleButton instance to pass into \ref datetime_control.datetime_control state of this widet will control appearance of the box\n
        \c box - gtk.Container instance to hide or show when chbt changed\n
        \c year - gtk.SpinButton instance to display year, pass to \ref datetime_control.datetime_control\n
        \c month - gtk.SpinButton instance to display month\n
        \c day - gtk.SpinButton instance\n
        \c calendar - gtk.Calendar instance to display date, passed into \ref datetime_control.datetime_control\n
        \c hour - gtk.SpinButton instance to display hour passed to \ref time_control.time_control\n
        \c min - gtk.SpinButton\n
        \c sec - gtk.SpinButton\n
        \c time_chbt - gtk.ToggleButton instance - checkbutton to control the show state of time_box\n
        \c time_box - gtk.Container instance, box with time controls - all that controled by \ref time_control.time_control
        \param upper hash table with same keys
        \param box - list of gtk.Container instances, boxes controled by checkbutton parameter state
        \param checkbutton - gtk.ToggleButton, when inactive widgets from box list will be hided
        """
        self.hiders = []
        for (bt, boxes) in [(checkbutton, box)] + reduce(lambda a, b: a + b, map(lambda h: [(gethash(h, "time_chbt"), [gethash(h, "time_box")]),
                                                                                            (gethash(h, "chbt"), [gethash(h, "box")])],
                                                                                 [lower, upper])):
            rbox = filter(lambda a: a != None, boxes)
            if bt != None and len(rbox) > 0:
                self.hiders.append(hide_control(bt, rbox))
        subhide = filter(lambda a: a != None, map(lambda b: gethash(b, "chbt"), [lower, upper]))
        if len(subhide) > 0 and checkbutton != None:
            self.subhide = all_checked_control(checkbutton, subhide)
        times = map(lambda h: time_control( *map(lambda k: gethash(h, k), ["hour", "min", "sec", "time_chbt"])),
                    [lower, upper])
        dtimes = map(lambda cal, time, chbt, year, month, day: datetime_control(cal, time, chbt, year, month, day),
                     map(lambda a: gethash(a, "calendar"), [lower, upper]),
                     times,
                     map(lambda a: gethash(a, "chbt"), [lower, upper]),
                     map(lambda a: gethash(a, "year"), [lower, upper]),
                     map(lambda a: gethash(a, "month"), [lower, upper]),
                     map(lambda a: gethash(a, "day"), [lower, upper]))
                     
        datetime_range_control.__init__(self, *(dtimes + [checkbutton]))
        



        
