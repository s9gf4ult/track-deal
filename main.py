#!/bin/env python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import gtk

class main_ui():
    def __init__(self):
        a = gtk.Builder()
        a.add_from_file("main_ui.glade")
        self.window = a.get_object("main_window")
        self.axce1 = a.get_object("get_axcel")
        self.segfault = a.get_object("get_seg")
        self.choose_file = a.get_object("choose_file")
        self.window.connect("destroy", gtk.main_quit)

    def show(self):
        self.window.show_all()


obj = main_ui()
obj.show()
gtk.main()
