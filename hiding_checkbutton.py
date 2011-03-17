#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class hiding_checkbutton():
    def __init__(self, name, subwidget, active = False, hide = True):
        self.to_hide = hide
        self.frame = gtk.Frame()
        self.checkbutton = gtk.CheckButton(name)
        self.subwidget = subwidget
        self.frame.set_label_widget(self.checkbutton)
        self.frame.add(subwidget)
        self.checkbutton.set_active(active)
        if active:
            if hide:
                subwidget.show()
            else:
                subwidget.set_sensitive(False)
        else:
            if hide:
                subwidget.hide()
            else:
                subwidget.set_sensitive(True)
        self.checkbutton.connect("toggled", self._toggled)
        self.subwidget.connect("show", self._on_show)

    def _toggled(self, tb):
        if tb.get_active():
            self.subwidget.show()
            self.subwidget.set_sensitive(True)
        else:
            if self.to_hide:
                self.subwidget.hide()
            else:
                self.subwidget.set_sensitive(False)

    def _on_show(self, wid):
        if not self.checkbutton.get_active():
            if self.to_hide:
                wid.hide()
            else:
                wid.set_sensitive(False)

    def get_widget(self):
        return self.frame

    def get_active(self):
        return self.checkbutton.get_active()

if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    vb = gtk.VBox()
    vb.pack_start(hiding_widget("check to hide", gtk.Label("hello")).get_widget(), False)
    vb.pack_start(hiding_widget("check another", gtk.Label("hi"), True).get_widget(), False)
    w.add(vb)
    w.show_all()
    gtk.main()
