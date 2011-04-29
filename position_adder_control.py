#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
from common_methods import *
from hide_control import hide_control
from datetime_start_end_control import *
from datetime_control import *
from time_control import *
from number_range_control import *
from combo_control import *
from select_control import *

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
        self.price = number_range_control(number_control(shorter("padder_open"), step_incr = 0.1, digits = 4),
                                          number_control(shorter("padder_close"), step_incr = 0.1, digits = 4))
        self.price.set_lower_limit(0)
        self.price.set_upper_limit(sys.float_info.max)

        self.broker_comm = number_range_control(number_control(shorter("padder_open_broker"), step_incr = 0.1, digits = 4),
                                                number_control(shorter("padder_close_broker"), step_incr = 0.1, digits = 4))
        self.broker_comm.set_lower_limit(0)
        self.broker_comm.set_upper_limit(sys.float_info.max)

        self.stock_comm = number_range_control(number_control(shorter("padder_open_stock"), step_incr = 0.1, digits = 4),
                                               number_control(shorter("padder_close_stock"), step_incr = 0.1, digits = 4))
        self.stock_comm.set_lower_limit(0)
        self.stock_comm.set_upper_limit(sys.float_info.max)

        self.instrument = combo_control(shorter("padder_ticket"))
        self.instrument_class = combo_control(shorter("padder_class"))
        self.long_short = select_control({-1 : shorter("padder_long"),
                                          1 : shorter("padder_short")})
        self.count =  number_control(shorter("padder_count"))
        self.count.set_lower_limit(0)
        self.count.set_upper_limit(sys.maxint)
                                                         

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
