#!/bin/env python
# -*- coding: utf-8 -*-

from od_exceptions import od_exception_parameter_error
from regexp_entry_control import regexp_entry_control
import gtk

class number_entry_control(regexp_entry_control):

    def pressed(self, entry, event):
        if event.type in [gtk.gdk._2BUTTON_PRESS, gtk.gdk._3BUTTON_PRESS]:
            entry.stop_emission('button-press-event')
    
    def _idle_select_before_dot(self):
        dotpos = self.entry.get_text().find('.')
        if dotpos >= 0:
            self.entry.select_region(0, dotpos)
        else:
            self._idle_select_all()
    
    def _idle_select_all(self):
        self.entry.select_region(0, -1)
    
    def _idle_select_after_dot(self):
        dotpos = self.entry.get_text().find('.')
        if dotpos >= 0:
            self.entry.select_region(dotpos + 1, -1)
        else:
            self._idle_select_all()
    
    def released(self, entry, event):
        pos = entry.get_position()
        dotpos = entry.get_text().find('.')
        if dotpos >= 0:
            if pos <= dotpos:
                gtk.idle_add(self._idle_select_before_dot)
            else:
                gtk.idle_add(self._idle_select_after_dot)
        else:
            gtk.idle_add(self._idle_select_all)
    
    def __init__(self, 
                 entry,
                 regexp = '^\d*(.\d*)?$',
                 initial = '0'):
        super(number_entry_control, self).__init__(entry, regexp, initial)
        entry.connect('button-press-event', self.pressed)
        entry.connect('button-release-event', self.released)

    def pre_stop_emission_hook(self, entry, new_text, signal_name):
        txt = entry.get_text()
        dotpos = txt.find('.')
        if dotpos < 0:
            return
        pos = entry.get_position()
        if dotpos == pos and new_text[pos: pos + 2] == '..': # if current position just before point and we try insert another
            gtk.idle_add(self._idle_select_after_dot)
        
    def get_value(self):
        return float(self.entry.get_text())
    
    def set_value(self, value):
        if isinstance(value, (int, float, long)):
            self.entry.set_text(str(value))
        elif isinstance(value, basestring):
            self.entry.set_text(str(float(value)))
        else:
            raise od_exception_parameter_error('value must be string or number')
        
    
if __name__ == "__main__":
    win = gtk.Dialog()
    p = win.get_content_area()
    en = gtk.Entry()
    p.pack_start(en, False)
    x = number_entry_control(en)
    bt = gtk.Button('get value')
    lbl = gtk.Label()

    def print_val(button):
        lbl.set_text(str(x.get_value()))
        
    bt.connect('clicked', print_val)
    p.pack_start(bt, False)
    p.pack_start(lbl, False)
    bt2 = gtk.Button('set value')
    en2 = gtk.Entry()
    p.pack_start(bt2, False)
    p.pack_start(en2, False)
    def set_val(button):
        x.set_value(en2.get_text())
    bt2.connect('clicked', set_val)
    win.show_all()
    win.run()
    win.hide()