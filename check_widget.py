#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from list_view_sort_control import *

class check_control():
    
    def __init__(self, treeview, first_column_name, columns, reverse_button = None, reverse_all_button = None, select_button = None, select_all_button = None, deselect_button = None, deselect_all_button = None):
        """columns must be a list of pairs with name and CellRenderer objects, but first
        column will be checkbutton column"""
        c = gtk.CellRendererToggle()
        c.props.activatable = True
        c.connect("toggled", self.row_toggled)
        self.list_control = list_view_sort_control(treeview, [(first_column_name, c)] + columns)
        self.treeview = treeview
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.reverse_button = reverse_button
        self.reverse_all_button = reverse_all_button
        self.select_button = select_button
        self.select_all_button = select_all_button
        self.deselect_button = deselect_button
        self.deselect_all_button = deselect_all_button

    def row_toggled(self, renderer, path):
        it = self.treeview.get_model().get_iter(path)
        val = self.treeview.get_model().get_value(it, 0)
        self.treeview.get_model().set_value(it, 0, not val)

    def reverse_foreach(self, t, p, i):
        val = self.list_store.get_value(i, 0)
        self.list_store.set_value(i, 0, not val)

    def unset_foreach(self, t, p, i):
        self.list_store.set_value(i, 0, False)

    def set_foreach(self, t, p, i):
        self.list_store.set_value(i, 0, True)
        
    def button_clicked(self, bt, callme):
        self.tree_view.get_selection().selected_foreach(callme)


    def flush_list(self):
        it = self.list_store.get_iter_first()
        while it:
            self.list_store.remove(it)
            it = self.list_store.get_iter_first()

    def update_widget(self, elt_list):
        found = {}
        it = self.list_store.get_iter_first()
        while it:
            found[self.list_store.get_value(it, 1).decode("utf-8")] = self.list_store.get_value(it, 0)
            it = self.list_store.iter_next(it)
        self.flush_list()
        for elt in elt_list:
            if found.has_key(elt.decode("utf-8")):
                bo = found[elt.decode("utf-8")]
            else:
                bo = True
            self.list_store.append([bo, elt])


if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    v = gtk.TreeView()
    p.pack_start(v)
    con = check_control(v, "Yes?", [("Name", gtk.CellRendererText())])
    con.list_control.update_rows([(True, "ijeij"), (False, "jfjfj")])
    w.show_all()
    w.run()
