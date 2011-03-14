#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class hiding_widget():
    def __init__(self, name, subwidget):
        self.frame = gtk.Frame()
        self.checkbox = gtk.CheckButton(name)
        self.frame.set_label(self.checkbox)
        
