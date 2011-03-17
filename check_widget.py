#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class check_widget():
    def __init__(self, the_name):
        self.vbox = gtk.VBox()
        self.list_store = gtk.ListStore(bool, str)
        self.tree_view = gtk.TreeView(self.list_store)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        tren = gtk.CellRendererToggle()
        tren.props.activatable = True
        tren.connect("toggled", self.row_toggled)
        self.tree_view.append_column(gtk.TreeViewColumn('', tren, active = 0))
        self.tree_view.append_column(gtk.TreeViewColumn(the_name, gtk.CellRendererText(), text = 1))
        sw = gtk.ScrolledWindow()
        sw.add(self.tree_view)
        self.vbox.pack_start(sw)
        self.reverse_button = gtk.Button(u'Реверс')
        self.unset_button = gtk.Button(u'Снять выделение')
        self.set_button = gtk.Button(u'Установить выделение')
        self.reverse_button.connect("clicked", self.button_clicked, self.reverse_foreach)
        self.unset_button.connect("clicked", self.button_clicked, self.unset_foreach)
        self.set_button.connect("clicked", self.button_clicked, self.set_foreach)
        self.hbb = gtk.HButtonBox()
        self.hbb.set_layout(gtk.BUTTONBOX_SPREAD)
        self.hbb.pack_start(self.reverse_button)
        self.hbb.pack_start(self.unset_button)
        self.hbb.pack_start(self.set_button)
        self.vbox.pack_start(self.hbb, False)

    def row_toggled(self, renderer, path):
        it = self.list_store.get_iter(path)
        val = self.list_store.get_value(it, 0)
        self.list_store.set_value(it, 0, not val)

    def reverse_foreach(self, t, p, i):
        val = self.list_store.get_value(i, 0)
        self.list_store.set_value(i, 0, not val)

    def unset_foreach(self, t, p, i):
        self.list_store.set_value(i, 0, False)

    def set_foreach(self, t, p, i):
        self.list_store.set_value(i, 0, True)
        
    def button_clicked(self, bt, callme):
        self.tree_view.get_selection().selected_foreach(callme)

    def get_widget(self):
        return self.vbox

    def flush_list(self):
        it = self.list_store.get_iter_first()
        while it:
            self.list_store.remove(it)
            it = self.list_store.get_iter_first()

    def update_widget(self, elt_list):
        found = {}
        it = self.list_store.get_iter_first()
        while it:
            found[self.list_store.get_value(it, 1)] = self.list_store.get_value(it, 0)
            it = self.list_store.iter_next(it)
        print(len(found))
        self.flush_list()
        for elt in elt_list:
            self.list_store.append([found.has_key(elt) and found[elt] or True, elt])


if __name__ == "__main__":
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    cw = check_widget(u'hello')
    for x in range(1, 100):
        cw.list_store.append([True, x])
    w.add(cw.get_widget())
    w.show_all()
    gtk.main()
