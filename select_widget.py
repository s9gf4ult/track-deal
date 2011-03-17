#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from hiding_checkbutton import hiding_checkbutton

class select_widget(hiding_checkbutton):
    def __init__(self, name, radios, vertical = True, expand = False, hide = True):
        self.radios = {}
        if vertical:
            box = gtk.VBox()
        else:
            box = gtk.HBox()
        for radio in radios:
            if len(self.radios) == 0:
                radiobutton = gtk.RadioButton(label = radios[radio])
            else:
                radiobutton = gtk.RadioButton(label = radios[radio], group = self.radios.keys()[0])
            self.radios[radiobutton] = radio
            box.pack_start(radiobutton, expand)

        hiding_checkbutton.__init__(self, name, box, hide = hide)

    def get_selected(self):
        if not self.checkbutton.get_active():
            return None
        else:
            for radio in self.radios:
                if radio.get_active():
                    return self.radios[radio]
        
if __name__ == "__main__":
    def clicked(bt, tb, sw):
        tb.set_text("{0}".format(sw.get_selected()))
    w = gtk.Window()
    w.connect("delete-event", gtk.main_quit)
    sw = select_widget('asdfa', {0: "hello" , 1 : "byby", 2: "ijij", 3 : "i2ji2j"})
    bt = gtk.Button("PUshme")
    tw = gtk.TextView()
    tb = tw.get_buffer()
    bt.connect("clicked", clicked, tb, sw)
    vbox = gtk.VBox()
    vbox.pack_start(sw.get_widget(), False)
    vbox.pack_start(tw, True)
    vbox.pack_start(bt, False)
    w.add(vbox)
    w.show_all()
    gtk.main()
