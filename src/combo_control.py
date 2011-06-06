#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import value_returner_control

class combo_control(value_returner_control):
    """controls combobox and comboedit with one interface
    you can easly update rows in combobox with update_widget"""
    def __init__(self, combobox, checkbutton = None):
        self.combobox = combobox
        self.checkbutton = checkbutton
        if not isinstance(self.combobox, gtk.ComboBoxEntry):
            cell = gtk.CellRendererText()
            self.combobox.pack_start(cell)
            self.combobox.add_attribute(cell, 'text', 0)

    def update_widget(self, rows):
        m = gtk.ListStore(str)
        for row in rows:
            m.append((row,))
        self.combobox.set_model(m)
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            self.combobox.set_text_column(0)

    def get_value(self):
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            return self.return_value(self.combobox.child.get_text())
        # elif isinstance(self.combobox, gtk.ComboBoxText):
        #     return self.return_value(self.combobox.get_active_text())
        else:
            return self.return_value(self.combobox.get_model().get_value(self.combobox.get_active_iter(), 0))

    def set_value(self, data):
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            self.combobox.child.set_text(data)
        elif isinstance(self.combobox, gtk.ComboBox):
            m = self.combobox.get_model()
            it = m.get_iter_first()
            while it != None:
                if m.get_value(it, 0).decode("utf-8") == data.decode("utf-8"):
                    self.combobox.set_active_iter(it)
                    return
                else:
                    it = m.iter_next(it)
            new = m.append((data,))
            self.combobox.set_active_iter(new)
                
            

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    c = gtk.ComboBox()
    p.pack_start(c)
    con = combo_control(c)
    con.update_widget(["ajaja", "fjfjfj", "rurur"])
    cc = gtk.ComboBoxEntry()
    p.pack_start(cc)
    ccon = combo_control(cc)
    ccon.update_widget(["cococoar", "ejejr", "eijwiej"])
    def pushed(bt):
        con.set_value("new_value")
    bt = gtk.Button("push")
    p.pack_start(bt)
    bt.connect("clicked", pushed)
    w.show_all()
    w.run()
