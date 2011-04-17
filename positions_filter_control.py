#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_number_range_control import hiding_number_range_control
from hiding_select_control import hiding_select_control
from hiding_datetime_range_control import hiding_datetime_range_control
from hiding_time_distance_range_control import *

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
        self.close_datetime = hiding_datetime_range_control({"chbt" : shorter("pfilter_close_datetime_lower"),
                                                            "box" : shorter("pfilter_close_datetime_lower_box"),
                                                            "calendar" : shorter("pfilter_close_datetime_lower_calendar"),
                                                            "hour" : shorter("pfilter_close_datetime_lower_hour"),
                                                            "min" : shorter("pfilter_close_datetime_lower_min"),
                                                            "sec" : shorter("pfilter_close_datetime_lower_sec"),
                                                            "time_chbt" : shorter("pfilter_close_datetime_lower_time"),
                                                            "time_box" : shorter("pfilter_close_datetime_lower_time_box")},
                                                           {"chbt" : shorter("pfilter_close_datetime_upper"),
                                                            "box" : shorter("pfilter_close_datetime_upper_box"),
                                                            "calendar" : shorter("pfilter_close_datetime_upper_calendar"),
                                                            "hour" : shorter("pfilter_close_datetime_upper_hour"),
                                                            "min" : shorter("pfilter_close_datetime_upper_min"),
                                                            "sec" : shorter("pfilter_close_datetime_upper_sec"),
                                                            "time_chbt" : shorter("pfilter_close_datetime_upper_time"),
                                                            "time_box" : shorter("pfilter_close_datetime_upper_time_box")},
                                                           [shorter("pfilter_close_datetime_lower_superbox"),
                                                            shorter("pfilter_close_datetime_upper_superbox")],
                                                           shorter("pfilter_close_datetime"))
                                                           

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
        self.price = hiding_number_range_control(shorter("pfilter_coast_lower_spin"),
                                                 shorter("pfilter_coast_upper_spin"),
                                                 shorter("pfilter_coast_box"),
                                                 shorter("pfilter_coast"),
                                                 shorter("pfilter_coast_lower"),
                                                 shorter("pfilter_coast_upper"))
        self.volume = hiding_number_range_control(shorter("pfilter_volume_lower_spin"),
                                                  shorter("pfilter_volume_upper_spin"),
                                                  shorter("pfilter_volume_box"),
                                                  shorter("pfilter_volume"),
                                                  shorter("pfilter_volume_lower"),
                                                  shorter("pfilter_volume_upper"))
        self.plnet_acc = hiding_number_range_control(shorter("pfilter_plnet_acc_lower_spin"),
                                                     shorter("pfilter_plnet_acc_upper_spin"),
                                                     shorter("pfilter_plnet_acc_box"),
                                                     shorter("pfilter_plnet_acc"),
                                                     shorter("pfilter_plnet_acc_lower"),
                                                     shorter("pfilter_plnet_acc_upper"))
        self.plnet_volume = hiding_number_range_control(shorter("pfilter_plnet_volume_lower_spin"),
                                                        shorter("pfilter_plnet_volume_upper_spin"),
                                                        shorter("pfilter_plnet_volume_box"),
                                                        shorter("pfilter_plnet_volume"),
                                                        shorter("pfilter_plnet_volume_lower"),
                                                        shorter("pfilter_plnet_volume_upper"))
        self.comm_plgross = hiding_number_range_control(shorter("pfilter_comm_plgross_lower_spin"),
                                                        shorter("pfilter_comm_plgross_upper_spin"),
                                                        shorter("pfilter_comm_plgross_box"),
                                                        shorter("pfilter_comm_plgross"),
                                                        shorter("pfilter_comm_plgross_lower"),
                                                        shorter("pfilter_comm_plgross_upper"))
        self.price_range = hiding_number_range_control(shorter("pfilter_price_range_lower_spin"),
                                                       shorter("pfilter_price_range_upper_spin"),
                                                       shorter("pfilter_price_range_box"),
                                                       shorter("pfilter_price_range"),
                                                       shorter("pfilter_price_range_lower"),
                                                       shorter("pfilter_price_range_upper"))
        self.plgross = hiding_number_range_control(shorter("pfilter_plgross_lower_spin"),
                                                   shorter("pfilter_plgross_upper_spin"),
                                                   shorter("pfilter_plgross_box"),
                                                   shorter("pfilter_plgross"),
                                                   shorter("pfilter_plgross_lower"),
                                                   shorter("pfilter_plgross_upper"))
        self.plnet = hiding_number_range_control(shorter("pfilter_plnet_lower_spin"),
                                                 shorter("pfilter_plnet_upper_spin"),
                                                 shorter("pfilter_plnet_box"),
                                                 shorter("pfilter_plnet"),
                                                 shorter("pfilter_plnet_lower"),
                                                 shorter("pfilter_plnet_upper"))
        self.comm = hiding_number_range_control(shorter("pfilter_comm_lower_spin"),
                                                shorter("pfilter_comm_upper_spin"),
                                                shorter("pfilter_comm_box"),
                                                shorter("pfilter_comm"),
                                                shorter("pfilter_comm_lower"),
                                                shorter("pfilter_comm_upper"))
        
        
        

        

        self.time_distance = hiding_time_distance_range_control({"chbt" : shorter("pfilter_timerange_lower"),
                                                                 "box" : shorter("pfilter_timerange_lower_box"),
                                                                 "day" : shorter("pfilter_timerange_lower_day"),
                                                                 "hour" : shorter("pfilter_timerange_lower_hour"),
                                                                 "min" : shorter("pfilter_timerange_lower_min")},
                                                                {"chbt" : shorter("pfilter_timerange_upper"),
                                                                 "box" : shorter("pfilter_timerange_upper_box"),
                                                                 "day" : shorter("pfilter_timerange_upper_day"),
                                                                 "hour" : shorter("pfilter_timerange_upper_hour"),
                                                                 "min" : shorter("pfilter_timerange_upper_min")},
                                                                [shorter("pfilter_timerange_lower_superbox"), shorter("pfilter_timerange_upper_superbox")],
                                                                shorter("pfilter_timerange"))

        
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
    
