#!/bin/env python
# -*- coding: utf-8 -*-

from time_control import time_control
from datetime_control import datetime_control
from datetime_range_control import datetime_range_control
from hide_control import *
from common_methods import *

class hiding_datetime_range_control(datetime_range_control):
    def __init__(self, lower, upper, box = None, checkbutton = None):
        self.hiders = []
        for (bt, boxes) in [(checkbutton, [box])] + reduce(lambda a, b: a + b, map(lambda h: [(gethash(h, "time_chbt"), [gethath(h, "time_box")]),
                                                                                              (gethash(h, "chbt"), [gethash(h, "box")])],
                                                                                   [lower, upper])):
            rbox = filter(lambda a: a != None, boxes)
            if bt != None and len(rbox) > 0:
                self.hiders.append(hide_control(bt, rbox))
        subhide = filter(lambda a: a != None, map(lambda b: gethash(b, "chbt"), [lower, upper]))
        if len(subhide) > 0 and checkbutton != None:
            self.subhide = all_checked_control(checkbutton, subhide)
        
        



        
