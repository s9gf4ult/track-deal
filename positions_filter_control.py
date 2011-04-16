#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_number_range_control import hiding_number_range_control
from hiding_select_control import hiding_select_control
from hiding_datetime_range_control import hiding_datetime_range_control

class positions_filter_control:
    def __init__(self, builder):
        self.builder = builder
        w = self.builder.get_object("positions_filter")
        w.add_buttons(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)
        def shorter(name):
            return self.builder.get_object(name)

        self.open_datetime = hiding_datetime_range_control({"chbt" : shorter("pfilter_open_datetime_lower"),
                                                            "box" : shorter("pfilter_open_datetime_lower_box"),
                                                            "calendar" : shorter("pfilter_open_datetime_lower_calendar"),
                                                            "hour" : shorter("pfilter_open_datetime_lower_hour"),
                                                            "min" : shorter("pfilter_open_datetime_lower_min"),
                                                            "sec" : shorter("pfilter_open_datetime_lower_sec"),
                                                            "time_chbt" : shorter("pfilter_open_datetime_lower_time"),
                                                            "time_box" : shorter("pfilter_open_datetime_lower_time_box")},
                                                           {"chbt" : shorter("pfilter_open_datetime_upper"),
                                                            "box" : shorter("pfilter_open_datetime_upper_box"),
                                                            "calendar" : shorter("pfilter_open_datetime_upper_calendar"),
                                                            "hour" : shorter("pfilter_open_datetime_upper_hour"),
                                                            "min" : shorter("pfilter_open_datetime_upper_min"),
                                                            "sec" : shorter("pfilter_open_datetime_upper_sec"),
                                                            "time_chbt" : shorter("pfilter_open_datetime_upper_time"),
                                                            "time_box" : shorter("pfilter_open_datetime_upper_time_box")},
                                                           [shorter("pfilter_open_datetime_lower_superbox"),
                                                            shorter("pfilter_open_datetime_upper_superbox")],
                                                           shorter("pfilter_open_datetime"))
                                                           

        self.direction = hiding_select_control({-1 : shorter("pfilter_direction_long"),
                                                1 : shorter("pfilter_direction_short")},
                                               shorter("pfilter_direction"),
                                               shorter("pfilter_direction_box"))
        self.count = hiding_number_range_control(shorter("pfilter_count_lower_spin"),
                                                 shorter("pfilter_count_upper_spin"),
                                                 shorter("pfilter_count_box"),
                                                 shorter("pfilter_count"),
                                                 shorter("pfilter_count_lower"),
                                                 shorter("pfilter_count_upper"))
                                                 

        
    def run(self):
        w = self.builder.get_object("positions_filter")
        w.show_all()
        w.run()
        w.hide()


if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = positions_filter_control(b)
    con.run()
    
