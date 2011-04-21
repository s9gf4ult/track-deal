#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import *
from time_distance_range_control import *
from common_methods import *

class hiding_time_distance_range_control(time_distance_range_control):
    def __init__(self, lower, upper, box = [], checkbutton = None):
        self.hiders = []
        for (chbt, boxes) in [(checkbutton, box),
                              (gethash(lower, "chbt"), gethash(lower, "box")),
                              (gethash(upper, "chbt"), gethash(upper, "box"))]:
            rbx = filter(lambda a: a != None, boxes)
            if chbt != None and len(rbx) > 0:
                self.hiders.append(hide_control(chbt, rbx))
        subh = filter(lambda a: a != None, [gethash(lower, "chbt"), gethash(upper, "chbt")])
        if len(subh) > 0 and checkbutton != None:
            self.subhider = all_checked_control(checkbutton, subh)
        ctrls = map(lambda h: time_distance_control(gethash(h, "day"), gethash(h, "hour"), gethash(h, "min"), checkbutton = gethash(h, "chbt")),
                    [lower, upper])
        time_distance_range_control.__init__(self, *(ctrls + [checkbutton]) )
