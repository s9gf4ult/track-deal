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
    def __init__(self, builder):
        self.builder = builder
        
        ######################
        # hide controls init #
        ######################
        self.hcontrols = []
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
            self.hcontrols.append(hide_control(self.builder.get_object(cb), map(lambda a: self.builder.get_object(a), boxes)))

        ##########################
        # checkbuttons subhiders #
        ##########################
        self.subhcontrols = []
        for (cb, subcbs) in [("deals_filter_datetime_range_cb", ["deals_filter_datetime_lower_cb", "deals_filter_datetime_upper_cb"]),
                             ("deals_filter_count_cb", ["deals_filter_count_lower_cb", "deals_filter_count_upper_cb"]),
                             ("deals_filter_price_cb", ["deals_filter_price_lower_cb", "deals_filter_price_upper_cb"]),
                             ("deals_filter_broker_comm_cb", ["deals_filter_broker_comm_lower_cb", "deals_filter_broker_comm_upper_cb"]),
                             ("deals_filter_stock_comm_cb", ["deals_filter_stock_comm_lower_cb", "deals_filter_stock_comm_upper_cb"]),
                             ("deals_filter_comm_cb", ["deals_filter_comm_lower_cb", "deals_filter_comm_upper_cb"]),
                             ("deals_filter_volume_cb", ["deals_filter_volume_lower_cb", "deals_filter_volume_upper_cb"])]:
            self.subhcontrols.append(all_checked_control(self.builder.get_object(cb), map(lambda a: self.builder.get_object(a), subcbs)))

        ####################
        # datetime control #
        ####################
        dtcontrols = []
        for (dtcb, dtcal, tcb, h, m, s) in [("deals_filter_datetime_lower_cb", "deals_filter_calendar_lower",
                                             "deals_filter_time_lower_cb", "deals_filter_hour_lower_spin",
                                             "deals_filter_min_lower_spin", "deals_filter_sec_lower_spin"),
                                            ("deals_filter_datetime_upper_cb", "deals_filter_calendar_upper",
                                             "deals_filter_time_upper_cb", "deals_filter_hour_upper_spin",
                                             "deals_filter_min_upper_spin", "deals_filter_sec_upper_spin")]:
            tcon = time_control(self.builder.get_object(h), self.builder.get_object(m), self.builder.get_object(s), self.builder.get_object(tcb))
            dtcon = datetime_control(self.builder.get_object(dtcal), tcon, self.builder.get_object(dtcb))
            dtcontrols.append(dtcon)
        self.datetime_range = datetime_range_control(dtcontrols[0], dtcontrols[1], self.builder.get_object("deals_filter_datetime_range_cb"))

        #############################
        # check instruments control #
        #############################
        dfv = self.builder.get_object("deals_filter_view")
        rev = self.builder.get_object("deals_filter_revers_bt")
        sel = self.builder.get_object("deals_filter_select_bt")
        desel = self.builder.get_object("deals_filter_deselect_bt")
        self.instruments = check_control(dfv, u'', [(u'Инструмент', gtk.CellRendererText())], reverse_button = rev, select_button = sel, deselect_button = desel)

        ###################
        # select controls #
        ###################
        self.position = select_control({self.builder.get_object("deals_filter_position_free_rb") : False,
                                        self.builder.get_object("deals_filter_position_occpied_rb") : True},
                                       self.builder.get_object("deals_filter_position_cb"))
        self.direction = select_control({self.builder.get_object("deals_filter_direction_long_rb") : -1,
                                         self.builder.get_object("deals_filter_direction_short_rb") : 1},
                                        self.builder.get_object("deals_filter_direction_cb"))
        
        ##################
        # number ranges  #
        ##################
        self.count = number_range_control(number_control(self.builder.get_object("deals_filter_count_lower_spin"),
                                                         self.builder.get_object("deals_filter_count_lower_cb")),
                                          number_control(self.builder.get_object("deals_filter_count_upper_spin"),
                                                         self.builder.get_object("deals_filter_count_upper_cb")),
                                          self.builder.get_object("deals_filter_count_cb"))
        self.price = number_range_control(number_control(self.builder.get_object("deals_filter_price_lower_spin"),
                                                         self.builder.get_object("deals_filter_price_lower_cb"), step_incr = 0.01, digits = 4),
                                          number_control(self.builder.get_object("deals_filter_price_upper_spin"),
                                                         self.builder.get_object("deals_filter_price_upper_cb"), step_incr = 0.01, digits = 4),
                                          self.builder.get_object("deals_filter_price_cb"))
        self.broker_comm = number_range_control(number_control(self.builder.get_object("deals_filter_broker_comm_lower_spin"),
                                                               self.builder.get_object("deals_filter_broker_comm_lower_cb"), step_incr = 0.01, digits = 4),
                                                number_control(self.builder.get_object("deals_filter_broker_comm_upper_spin"),
                                                               self.builder.get_object("deals_filter_broker_comm_upper_cb"), step_incr = 0.01, digits = 4),
                                                self.builder.get_object("deals_filter_broker_comm_cb"))
        self.stock_comm = number_range_control(number_control(self.builder.get_object("deals_filter_stock_comm_lower_spin"),
                                                              self.builder.get_object("deals_filter_stock_comm_lower_cb"), step_incr = 0.01, digits = 4),
                                               number_control(self.builder.get_object("deals_filter_stock_comm_upper_spin"),
                                                              self.builder.get_object("deals_filter_stock_comm_upper_cb"), step_incr = 0.01, digits = 4),
                                               self.builder.get_object("deals_filter_stock_comm_cb"))
        self.comm = number_range_control(number_control(self.builder.get_object("deals_filter_comm_lower_spin"),
                                                        self.builder.get_object("deals_filter_comm_lower_cb"), step_incr = 0.01, digits = 4),
                                         number_control(self.builder.get_object("deals_filter_comm_upper_spin"),
                                                        self.builder.get_object("deals_filter_comm_upper_cb"), step_incr = 0.01, digits = 4),
                                         self.builder.get_object("deals_filter_comm_cb"))
        self.volume = number_range_control(number_control(self.builder.get_object("deals_filter_volume_lower_spin"),
                                                          self.builder.get_object("deals_filter_volume_lower_cb"), digits = 4),
                                           number_control(self.builder.get_object("deals_filter_volume_upper_spin"),
                                                          self.builder.get_object("deals_filter_volume_upper_cb"),  digits = 4),
                                           self.builder.get_object("deals_filter_volume_cb"))
            
    def run(self):
        w = self.builder.get_object("deals_filter")
        w.show_all()
        w.run()

    def update_widget(self, count_range = None, price_range = None, broker_comm_range = None, stock_comm_range = None,
                      comm_range = None, volume_range = None, stock_list = None):
        for (control, rval) in [(self.count, count_range),
                                (self.price, price_range),
                                (self.broker_comm, broker_comm_range),
                                (self.stock_comm, stock_comm_range),
                                (self.comm, comm_range),
                                (self.volume, volume_range)]:
            if rval != None:
                control.set_lower_limit(rval[0])
                control.set_upper_limit(rval[1])
        if stock_list != None:
            self.instruments.update_rows(map(lambda a: (a,), stock_list))
    
                            
                            
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    d = deals_filter_control(b)
    d.update_widget(count_range = [0, 100], price_range = [10, 200], broker_comm_range = [0.1, 3], stock_comm_range = [0.01, 0.4], comm_range = [0.5, 0.6], volume_range = [100, 1000], stock_list = [u'Газик', u'Сберик', u'Полиметальчик'])
    d.run()
