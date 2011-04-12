#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import value_returner_control

class select_control(value_returner_control):
    def __init__(self, answers, checkbutton = None):
        self.answers = answers
        self.checkbutton = checkbutton

    def get_value(self):
        ret = None
        for k in self.answers:
            if self.answers[k].get_active():
                ret = k
                break
        return self.return_value(ret)

    def set_value(self, val):
        self.answers[val].set_active(True)
            
if __name__ == "__main__":
    w = gtk.Dialog(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    p = w.get_content_area()
    c = gtk.CheckButton("Do that")
    ans = {0 : gtk.RadioButton(label = "0")}
    for x in xrange(1, 5):
        yo = gtk.RadioButton(label = str(x), group = ans[0])
        ans[x] = yo
    scon = select_control(ans, c)
    p.pack_start(c, False)
    for x in ans:
        p.pack_start(ans[x], False)
    ent = gtk.Entry()
    def clicked(bt):
        ent.set_text("{0}".format(scon.get_value()))
    b = gtk.Button("push")
    b.connect("clicked", clicked)
    p.pack_start(ent, False)
    p.pack_start(b)
    w.show_all()
    w.run()

