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
        if self.reverse_button:
            self.reverse_button.connect("clicked", self.selection_button_clicked, self.reverse_foreach)
        self.reverse_all_button = reverse_all_button
        if self.reverse_all_button:
            self.reverse_all_button.connect("clicked", self.all_button_clicked, self.reverse_foreach)
        self.select_button = select_button
        if self.select_button:
            self.select_button.connect("clicked", self.selection_button_clicked, self.set_foreach)
        self.select_all_button = select_all_button
        if self.select_all_button:
            self.select_all_button.connect("clicked", self.all_button_clicked, self.set_foreach)
        self.deselect_button = deselect_button
        if self.deselect_button:
            self.deselect_button.connect("clicked", self.selection_button_clicked, self.unset_foreach)
        self.deselect_all_button = deselect_all_button
        if self.deselect_all_button:
            self.deselect_all_button.connect("clicked", self.all_button_clicked, self.unset_foreach)

    def row_toggled(self, renderer, path):
        it = self.treeview.get_model().get_iter(path)
        val = self.treeview.get_model().get_value(it, 0)
        self.treeview.get_model().set_value(it, 0, not val)

    def reverse_foreach(self, x, y, i):
        m = self.treeview.get_model()
        val = m.get_value(i, 0)
        m.set_value(i, 0, not val)

    def unset_foreach(self, x, u, i):
        self.treeview.get_model().set_value(i, 0, False)

    def set_foreach(self, x, y, i):
        self.treeview.get_model().set_value(i, 0, True)
        
    def selection_button_clicked(self, bt, callme):
        self.treeview.get_selection().selected_foreach(callme)

    def all_button_clicked(self, bt, callme):
        self.treeview.get_model().foreach(callme)


    def flush_list(self):
        m = self.treeview.get_model()
        it = m.get_iter_first()
        while it:
            m.remove(it)
            it = m.get_iter_first()

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
    sa = gtk.Button("select all")
    ss = gtk.Button("select")
    da = gtk.Button("deselect all")
    dd = gtk.Button("deselect")
    ra = gtk.Button("reverse all")
    rr = gtk.Button("reverse")
    for wid in [sa, ss, da, dd, ra, rr]:
        p.pack_start(wid)
    con = check_control(v, "Yes?", [("Name", gtk.CellRendererText())], select_button = ss, select_all_button = sa, deselect_button = dd, deselect_all_button = da, reverse_button = rr, reverse_all_button = ra)
    con.list_control.update_rows([(True, "One"), (False, "Two"), (True, "2 + 2 = 4"), (False, "3*5 = 14"), (True, "jojojo")])
    w.show_all()
    w.run()
