#!/bin/env python
# -*- coding: utf-8 -*-

from common_methods import find_in_list, find_in_model
from hide_control import value_returner_control
import gtk

class combo_select_control(value_returner_control):
    """
    \brief control for selecting value by representing string

    Uses combobox to display string and when this string is selected assigned value can be returned
    """
    def __init__(self, combobox, answers = None, none_answer = None, checkbutton = None, use_completion = True):
        """
        \param combobox gtk.ComboBox instance or gtk.ComboBoxEntry, if second then use_completion can be used
        \param answers list of tuples (value, string), string will be displayed in combobox, value will be returned by \ref get_value
        \param none_answer - value for returning if empty item is selected
        \param checkbutton - gtk.ToggleButton instance
        """
        self.checkbutton = checkbutton
        self.combobox = combobox
        self.none_answer = none_answer
        if not (use_completion and isinstance(combobox.get_child(), gtk.Entry)):
            c = gtk.CellRendererText()
            self.combobox.pack_start(c)
            self.combobox.add_attribute(c, "text", 1)
        self.use_completion = use_completion
        if answers != None:
            self.update_answers(answers, none_answer)

    def update_answers(self, answers, none_answer = None):
        """
        \brief set new answers set
        \param answers list of tuples like for \ref __init__
        \param none_answer - value to return when empty item is selected
        """
        if answers == None:
            return
        if len(answers) == 0:
            m = gtk.ListStore(int, str)
            self.combobox.set_model(m)
            if self.use_completion and isinstance(self.combobox.get_child(), gtk.Entry):
                self.combobox.get_child().set_completion(None)
            return
        self.none_answer = none_answer
        val = self.get_value()
        m = gtk.ListStore(isinstance(answers[0][0], basestring) and str or type(answers[0][0]), str)
        for a in answers:
            m.append(a)
        if none_answer != None:
            m.append((none_answer, ""))
        self.combobox.set_model(m)
        if self.use_completion and isinstance(self.combobox.get_child(), gtk.Entry):
            ent = self.combobox.get_child()
            completion = gtk.EntryCompletion()
            completion.set_model(m)
            completion.set_text_column(1)
            completion.set_inline_completion(True)
            ent.set_completion(completion)
            self.combobox.set_entry_text_column(1)
        if val != None:
            fnd = find_in_list(lambda a: a[0] == val, answers)
            if fnd != None:
                self.combobox.set_active(fnd)

    def set_value(self, val):
        """
        \brief set value if exists in answers
        \param val - value to set
        \retval True - value found and set
        \retval False - value was not found
        """
        m = self.combobox.get_model()
        if m != None:
            itt = find_in_model(m, lambda mod, it: mod.get_value(it, 0) == val)
            if itt != None:
                self.combobox.set_active_iter(itt)
                return True
        return False
                                 

    def get_value(self):
        """
        \brief get selected value
        \retavl None if checkbutton is not active
        \retval value assigned to selected in combobox string
        """
        if self.combobox.get_model() == None:
            return None
        if isinstance(self.combobox.get_child(), gtk.Entry): # we have entry in combobox
            val = self.combobox.get_active_text()
            model = self.combobox.get_model()
            fit = find_in_model(model, lambda mod, itt: mod.get_value(itt, 1) == val)
            if fit == None:
                return self.return_value(self.none_answer)
            return self.return_value(model.get_value(fit, 0))
        else: # we have not entry in combobox
            it = self.combobox.get_active_iter()
            if it != None:
                val = self.combobox.get_model().get_value(it, 0)
                return self.return_value(val)
            return self.return_value(self.none_answer)

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    b = gtk.ComboBox()
    p.pack_start(b)
    bubu = gtk.CheckButton()
    p.pack_start(bubu)
    con = combo_select_control(b, [(100, "hundred"), (200, "two hundred")], none_answer = -1, checkbutton = bubu)
    bt = gtk.Button("push")
    p.pack_start(bt)
    def push(bt):
        con.update_answers([(20, "eeje"), (200, "200"), (300, "300"), (100, "100")], none_answer = -1)
    bt.connect("clicked", push)
    btt = gtk.Button("push this")
    def btt_push(bt):
        con.set_value(200)
    btt.connect("clicked", btt_push)
    p.pack_start(btt)
    lbl = gtk.Label()
    def some_clicked(bt):
        lbl.set_text(str(con.get_value()))
    vub = gtk.Button("show")
    vub.connect("clicked", some_clicked)
    p.pack_start(lbl)
    p.pack_start(vub)
    w.show_all()
    w.run()
    print(con.get_value())
