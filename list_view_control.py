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
            c = gtk.TreeViewColumn(title = columns[k][0], cell_renderer = columns[k][1], **prop)
            c.set_clickable(True)
            c.connect("clicked", self.column_clicked, k)
            self.treeview.append_column(c)
            
    def make_model(self):
        m = gtk.ListStore(*self.model_columns)
        
        
