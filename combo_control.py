#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class combo_control:
    def __init__(self, combobox):
        self.combobox = combobox
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
            return self.combobox.get_text()
        elif isinstance(self.combobox, gtk.ComboBoxText):
            return self.combobox.get_active_text()
        else:
            return self.combobox.get_model().get_value(self.combobox.get_active_iter(), 0)

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
    w.show_all()
    w.run()