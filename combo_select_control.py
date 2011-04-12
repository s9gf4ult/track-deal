#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from common_methods import *

class combo_select_control:
    def __init__(self, combobox, answers = None, none_answer = None):
        self.combobox = combobox
        self.none_answer = none_answer
        c = gtk.CellRendererText()
        self.combobox.pack_start(c)
        self.combobox.add_attribute(c, "text", 1)
        if answers != None:
            self.update_widget(answers, none_answer)

    def update_widget(self, answers, none_answer = None):
        self.none_answer = none_answer
        val = self.get_value()
        m = gtk.ListStore(answers[0][0].__class__, str)
        for a in answers:
            m.append(a)
        if none_answer != None:
            m.append((none_answer, ""))
        self.combobox.set_model(m)
        if val != None:
            fnd = find_in_list(lambda a: a[0] == val, answers)
            if fnd != None:
                self.combobox.set_active(fnd)
            

    def get_value(self):
        if self.combobox.get_model() == None:
            return None
        it = self.combobox.get_active_iter()
        if it != None:
            val = self.combobox.get_model().get_value(it, 0)
            if self.none_answer != None and val == self.none_answer:
                return None
            else:
                return val
        return None

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    b = gtk.ComboBox()
    p.pack_start(b)
    con = combo_select_control(b, [(100, "hundred"), (200, "two hundred")], none_answer = -1)
    bt = gtk.Button("push")
    p.pack_start(bt)
    def push(bt):
        con.update_widget([(20, "eeje"), (200, "200"), (300, "300"), (100, "100")], none_answer = -1)
    bt.connect("clicked", push)
    w.show_all()
    w.run()
    print(con.get_value())
