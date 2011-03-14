#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class deals_filter_dialog():

    def hider_toggled(self, tg, hide):
        if tg.get_active():
            hide.show_all()
        else:
            hide.hide()

    def activator_toggled(self, tg, act):
        act.set_editable(tg.get_active())
        
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file('deals_filter_dialog.glade')
        for x in [("direction_checkbox", self.hider_toggled, "direction_box"),
                  ("position_checkbox", self.hider_toggled, "position_box"),
                  ("price_checkbox", self.hider_toggled, "price_box")]:
            tb = self.builder.get_object(x[0])
            hb = self.builder.get_object(x[2])
            hb.hide()
            tb.set_active(False)
            tb.connect("toggled", x[1], hb)
        for x in [("price_more_checkbox", self.activator_toggled, "spinbutton1"),
                  ("price_less_checkbox", self.activator_toggled, "spinbutton2")]:
            tb = self.builder.get_object(x[0])
            eb = self.builder.get_object(x[2])
            eb.set_editable(False)
            tb.set_active(False)
            tb.connect("toggled", self.activator_toggled, eb)

    

    def show(self):
        win = self.builder.get_object("main_window")
        win.show()
        pass

    
if __name__ == "__main__":
    df = deals_filter_dialog()
    df.show()
    gtk.main()
