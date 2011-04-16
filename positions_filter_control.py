#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_number_range_control import hiding_number_range_control

class positions_filter_control:
    def __init__(self, builder):
        self.builder = builder
        w = self.builder.get_object("positions_filter")
        w.add_buttons(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)
        def shorter(name):
            return self.builder.get_object(name)
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
    
