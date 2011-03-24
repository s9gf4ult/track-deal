#!/bin/env python
# -*- coding: utf-8 -*-

class hide_control:
    def __init__(self, checkbutton, hide_widget, hide = False):
        self.checkbutton = checkbutton
        self.hide_widget = hide_widget
        self.hide = hide
        self.checkbutton.connect("toggled", self.toggled)
        if self.checkbutton.get_active():
            if self.hide:
                self.hide_widget.show()
            else:
                self.hide_widget.set_sensitive(True)
        else:
            if self.hide:
                self.hide_widget.hide()
            else:
                self.hide_widget.set_sensitive(False)

    def toggled(self, chbut):
        if chbut.get_active():
            
        
        
