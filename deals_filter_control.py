#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hide_control import *
from datetime_control import *
from datetime_range_control import *
from time_control import *
from check_control import *
from select_control import *
from number_range_control import *

class deals_filter_control:
    def __init__(self, builder, database):
        self.builder = builder
        self.database = database

        ######################
        # hide controls init #
        ######################
        for (cb, boxes) in [("deals_filter_datetime_range_cb", ["deals_filter_datetime_range_box"]),
                            ("deals_filter_datetime_lower_cb", ["deals_filter_calendar_lower", "deals_filter_lower_time_box"]),
                            ("deals_filter_datetime_upper_cb", ["deals_filter_calendar_upper", "deals_filter_upper_time_box"]),
                            ("deals_filter_time_lower_cb", ["deals_filter_time_lower_box"]),
                            ("deals_filter_time_upper_cb", ["deals_filter_time_upper_box"]),
                            ("deals_filter_position_cb", ["deals_filter_position_box"]),
                            ("deals_filter_direction_cb", ["deals_filter_direction_box"]),
                            ("deals_filter_count_cb", ["deals_filter_count_box"]),
                            ("deals_filter_price_cb", ["deals_filter_price_box"]),
                            ("deals_filter_broker_comm_cb", ["deals_filter_broker_comm_box"]),
                            ("deals_filter_stock_comm_cb", ["deals_filter_stock_comm_box"]),
                            ("deals_filter_comm_cb", ["deals_filter_comm_box"]),
                            ("deals_filter_volume_cb", ["deals_filter_volume_box"]),
                            ("deals_filter_count_lower_cb", ["deals_filter_count_lower_spin"]),
                            ("deals_filter_count_upper_cb", ["deals_filter_count_upper_spin"]),
                            ("deals_filter_price_lower_cb", ["deals_filter_price_lower_spin"]),
                            ("deals_filter_price_upper_cb", ["deals_filter_price_upper_spin"]),
                            ("deals_filter_broker_comm_lower_cb", ["deals_filter_broker_comm_lower_spin"]),
                            ("deals_filter_broker_comm_upper_cb", ["deals_filter_broker_comm_upper_spin"]),
                            ("deals_filter_stock_comm_lower_cb", ["deals_filter_stock_comm_lower_spin"]),
                            ("deals_filter_stock_comm_upper_cb", ["deals_filter_stock_comm_upper_spin"]),
                            ("deals_filter_comm_lower_cb", ["deals_filter_comm_lower_spin"]),
                            ("deals_filter_comm_upper_cb", ["deals_filter_comm_upper_spin"]),
                            ("deals_filter_volume_lower_cb", ["deals_filter_volume_lower_spin"]),
                            ("deals_filter_volume_upper_cb", ["deals_filter_volume_upper_spin"])]:
            print(cb)
            hide_control(self.builder.get_object(cb), map(lambda a: self.builder.get_object(a), boxes))
            
    def run(self):
        w = self.builder.get_object("deals_filter")
        w.show_all()
        w.run()
                            
                            
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    d = deals_filter_control(b, 10)
    d.run()
    
