#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class hide_control:
    def __init__(self, checkbutton, hide_widgets, hide = False, reverse = False):
        self.checkbutton = checkbutton
        self.hide_widgets = hide_widgets
        self.hide = hide
        self.reverse = reverse
        self.checkbutton.connect("toggled", self.toggled)
        for w in self.hide_widgets:
            w.connect("show", self.toggled)
        self.toggled(None)

    def hide_all(self):
        for w in self.hide_widgets:
            w.hide()

    def show_all(self):
        for w in self.hide_widgets:
            w.show()

    def set_sensitive_all(self, sens):
        for w in self.hide_widgets:
            w.set_sensitive(sens)

    def toggled(self, something):
        p = self.checkbutton.get_active()
        if self.reverse:
            p = not p
        if p:
            if self.hide:
                self.show_all()
            else:
                self.set_sensitive_all(True)
        else:
            if self.hide:
                self.hide_all()
            else:
                self.set_sensitive_all(False)

class all_checked_control:
    def __init__(self, parent_checkbutton, child_checkbuttons):
        self.parent_checkbutton = parent_checkbutton
        self.child_checkbuttons = child_checkbuttons
        for w in self.child_checkbuttons:
            w.connect("toggled", self.toggled)
        self.toggled(None)

    def toggled(self, something):
        for w in self.child_checkbuttons:
            if w.get_active():
                return
        self.parent_checkbutton.set_active(False)
        
class value_returner_control:
    def return_value(self, value):
        if self.checkbutton:
            if self.checkbutton.get_active():
                return value
        else:
            return value
        return None


if __name__ == "__main__":
    w = gtk.Dialog(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    p = w.get_content_area()
    c = gtk.CheckButton("eijeifj")
    b = gtk.Button("eifjefij")
    p.pack_start(c, False)
    p.pack_start(b)
    hide_control(c, [b])
    cc = gtk.ToggleButton("yayaya")
    bb = gtk.Label("super yagoo")
    bbb = gtk.Label("another super")
    p.pack_start(cc)
    p.pack_start(bb, False)
    p.pack_start(bbb, False)
    hide_control(cc, [bb, bbb], hide = True)
    pc = gtk.CheckButton("Dady")
    all_checked_control(pc, [c, cc])
    p.pack_start(pc, False)
    w.show_all()
    w.run()
