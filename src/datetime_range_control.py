#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import datetime
from hide_control import value_returner_control

class datetime_range_control(value_returner_control):
    def __init__(self, lower_datetime_control, upper_datetime_control, checkbutton = None):
        self.checkbutton = checkbutton
        self.lower_datetime_control = lower_datetime_control
        self.upper_datetime_control = upper_datetime_control
                 

    def get_lower_datetime(self):
        lt = self.lower_datetime_control.get_time()
        ld = self.lower_datetime_control.get_date()
        if lt == None:
            lt = datetime.time.min
        if ld != None:
            return self.return_value(datetime.datetime.combine(ld, lt))
        return None
            
    def get_upper_datetime(self):
        ut = self.upper_datetime_control.get_time()
        ud = self.upper_datetime_control.get_date()
        if ut == None:
            ut = datetime.time.max
        if ud != None:
            return self.return_value(datetime.datetime.combine(ud, ut))
        return None
