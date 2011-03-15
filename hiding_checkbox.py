#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class hiding_widget():
    def __init__(self, name, subwidget, active = False):
        self.frame = gtk.Frame()
        self.checkbutton = gtk.CheckButton(name)
        self.subwidget = subwidget
        self.frame.set_label_widget(self.checkbutton)
        self.frame.add(subwidget)
        self.checkbutton.set_active(active)
        if active:
            subwidget.show()
        else:
            subwidget.hide()
        self.checkbutton.connect("toggled", self._toggled)
        self.subwidget.connect("show", self._on_show)

    def _toggled(self, tb):
        if tb.get_active():
            self.subwidget.show()
        else:
            self.subwidget.hide()

    def _on_show(self, wid):
        if not self.checkbutton.get_active():
            wid.hide()

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
