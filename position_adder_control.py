#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from common_methods import *
from hide_control import hide_control

class position_adder_control:
    def __init__(self, builder):
        self.builder = builder
        def shorter(name):
            return self.builder.get_object(name)
        self.hiders = [hide_control(shorter("padder_calendars"), [shorter("padder_lower_calendar"), shorter("padder_upper_calendar")], hide = True)]

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
