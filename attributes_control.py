#!/bin/env python
# -*- coding: utf-8 -*-

from list_view_sort_control import list_view_sort_control
import gtk

class attributes_control:
    def __init__(self, treeview, name_entry, val_entry, add_button, del_button):
        self.treeview = treeview,
        self.name_entry = name_entry
        self.val_entry = val_entry
        self.add_button = add_button
        self.del_button = del_button
        self.attributes = list_view_sort_control(self.treeview, [(u'Имя', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
        self.add_button.connect("clicked", self.add_clicked)
        self.del_button.connect("clicked", self.del_clicked)
        self.treeview.connect("cursor-changed", self.cursor_changed)

    def add_clicked(self, bt):
        if len(self.name_entry.get_text()) > 0:
            self.attributes.add_rows([(self.name_entry.get_text(), self.val_entry.get_text())])

    def del_clicked(self, bt):
        (mod, it) = self.treeview.get_selection().get_selected()
        if it != None:
            mod.remove(it)

    def cursor_changed(self, tw):
        (mod, it) = self.treeview.get_selection().get_selected()
        if it != None:
            self.name_entry.set_text(mod.get_value(it, 0))
            self.val_entry.set_text(mod.get_value(it, 1))
            
            
