#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import datetime
from hide_control import value_returner_control

class datetime_range_control(value_returner_control):
    """
    \brief control to get datetime range
    """
    def __init__(self, lower_datetime_control, upper_datetime_control, checkbutton = None):
        """
        \param lower_datetime_control - \ref datetime_control.datetime_control instance to get lower limit of range
        \param upper_datetime_control - same as above for upper limit
        \param checkbutton - gtk.ToggleButton instance to control returning value
        """
        self.checkbutton = checkbutton
        self.lower_datetime_control = lower_datetime_control
        self.upper_datetime_control = upper_datetime_control
                 

    def get_lower_datetime(self):
        """
        \retval None if checkbutton is not active
        \retval datetime.datetime instance, value of the lower limit of the range
        """
        lt = self.lower_datetime_control.get_time()
        ld = self.lower_datetime_control.get_date()
        if lt == None:
            lt = datetime.time.min
        if ld != None:
            return self.return_value(datetime.datetime.combine(ld, lt))
        return None
            
    def get_upper_datetime(self):
        """
        \retval None if checkbutton is not active
        \retval datetime.datetime instance, value of the upper limit of the range
        """
        ut = self.upper_datetime_control.get_time()
        ud = self.upper_datetime_control.get_date()
        if ut == None:
            ut = datetime.time.max
        if ud != None:
            return self.return_value(datetime.datetime.combine(ud, ut))
        return None
