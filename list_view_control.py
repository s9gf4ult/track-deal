#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class list_view_control:
    def __init__(self, treeview, columns):
        """columns must be list of tuples with name and renderer, order of tuple in the list
        determines the order of columns in TreeView"""
        self.treeview = treeview
        self.model_columns = []
        for k in xrange(0, len(columns)):
            prop = {}
            if isinstance(columns[k][1], gtk.CellRendererText):
                prop["text"] = k
                if isinstance(columns[k][1], gtk.CellRendererSpin):
                    self.model_columns.append(float)
                else:
                    self.model_columns.append(str)
            elif isinstance(columns[k][1], gtk.CellRendererProgress):
                prop["value"] = k
                self.model_columns.append(float)
            elif isinstance(columns[k][1], gtk.CellRendererToggle):
                prop["active"] = k
                self.model_columns.append(bool)
            elif isinstance(columns[k][1], gtk.CellRendererPixbuf):
                prop["pixbuf"] = k
                self.model_columns.append(gtk.gdk.Pixbuf)
            c = gtk.TreeViewColumn(columns[k][0], columns[k][1], **prop)
            c.set_clickable(True)
            c.connect("clicked", self.column_clicked, k)
            self.treeview.append_column(c)
            
    def make_model(self):
        m = self.get_new_store()
        self.treeview.set_model(m)

    def get_new_store(self):
        return gtk.ListStore(*self.model_columns)
        
    def column_clicked(self, column, col_id):
        order = self.toggle_sort_indicator(col_id)
        if order != None:
            self.treeview.get_model().set_sort_column_id(col_id, order)

    def toggle_sort_indicator(self, col_id):
        for col in xrange(0, len(self.treeview.get_columns())):
            if col != col_id:
                self.treeview.get_column(col).set_sort_indicator(False)
        c = self.treeview.get_column(col_id)
        if c.get_sort_indicator():
            if c.get_sort_order() == gtk.SORT_ASCENDING:
                c.set_sort_order(gtk.SORT_DESCENDING)
                return gtk.SORT_DESCENDING
            else:
                c.set_sort_indicator(False)
                return None
        else:
            c.set_sort_indicator(True)
            c.set_sort_order(gtk.SORT_ASCENDING)
            return gtk.SORT_ASCENDING
                

    def update_rows(self, rows):
        m = self.get_new_store()
        for row in rows:
            m.append(row)
        self.treeview.set_model(m)

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    v = gtk.TreeView()
    p.pack_start(v)
    con = list_view_control(v, [("OK", gtk.CellRendererToggle()), ("Name", gtk.CellRendererText())])
    con.update_rows([(True, "ijij"), (True, "isejfj"), (False, "jeifjjj2")])
    w.show_all()
    w.run()
    
