#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class positions_filter_control:
    def __init__(self, builder):
        self.builder = builder
        w = self.builder.get_object("positions_filter")
        w.add_buttons(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)

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
    
