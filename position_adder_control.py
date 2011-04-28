#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from common_methods import *
from hide_control import hide_control
from datetime_start_end_control import *
from datetime_control import *
from time_control import *

class position_adder_control:
    def __init__(self, builder):
        self.builder = builder
        def shorter(name):
            return self.builder.get_object(name)
        self.hiders = [hide_control(shorter("padder_calendars"), [shorter("padder_lower_calendar"), shorter("padder_upper_calendar")], hide = True)]
        self.start_date = datetime_control(shorter("padder_lower_calendar"),
                                           time_control(*map(lambda a: shorter(u'padder_lower_{0}'.format(a)), ["hour", "min", "sec"])),
                                           year = shorter("padder_lower_year"),
                                           month = shorter("padder_lower_month"),
                                           day = shorter("padder_lower_day"))
        
        self.end_date = datetime_control(shorter("padder_upper_calendar"),
                                         time_control(*map(lambda a: shorter(u'padder_upper_{0}'.format(a)), ["hour", "min", "sec"])),
                                         year = shorter("padder_upper_year"),
                                         month = shorter("padder_upper_month"),
                                         day = shorter("padder_upper_day"))
                                           
        self.datetime_start_end = datetime_start_end_control(self.start_date, self.end_date)

    def run(self):
        w = self.builder.get_object("padder")
        w.show_all()
        ret = w.run()
        w.hide()
        return ret


if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = position_adder_control(b)
    con.run()
