#!/bin/env python
# -*- coding: utf-8 -*-

from list_view_sort_control import list_view_sort_control
import gtk

class attributes_control:
    def __init__(self, treeview, name_entry, val_entry, add_button, del_button):
        self.treeview = treeview
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
            has = map(lambda a: a[0].decode('utf-8'), self.attributes.get_rows())
            if self.name_entry.get_text().decode('utf-8') not in has:
                self.attributes.add_rows([(self.name_entry.get_text(), self.val_entry.get_text())])

    def del_clicked(self, bt):
        self.attributes.delete_selected()

    def cursor_changed(self, tw):
        selected = self.attributes.get_selected_row()
        if selected != None:
            self.name_entry.set_text(selected[0])
            self.val_entry.set_text(selected[1])

    def get_attributes(self):
        """
        \return hash table with attributes {key : value}
        """
        ret = {}
        ats = self.attributes.get_rows()
        for at in ats:
            ret[at[0]] = at[1]
        return ret

            
    def set_attributes(self, attributes):
        """
        \param attributes has table {key : value}
        """
        u = []
        x = attributes.keys()
        x.sort()
        for at in x:
            u.append((at, attributes[at]))
        self.attributes.update_rows(u)

    def flush(self):
        self.attributes.update_rows([])
        self.name_entry.set_text('')
        self.val_entry.set_text('')
