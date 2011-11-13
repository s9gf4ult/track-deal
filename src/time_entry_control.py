#!/bin/env python
# -*- coding: utf-8 -*-

from common_methods import print_error
from datetime import time, datetime
from od_exceptions import od_exception_parameter_error
from regexp_entry_control import regexp_entry_control
import gtk
import re

class time_entry_control(regexp_entry_control):
    
    def _idle_select_minute(self):
        self.entry.select_region(3, 5)
        
    def _idle_select_second(self):
        self.entry.select_region(6, 8)
        
    def _idle_select_hour(self):
        self.entry.select_region(0, 2)

    def changed(self, entry):
        if re.match('^\d{2}:\d{2}:\d{2}$', entry.get_text()):
            pos = entry.get_position()
            if pos == 1:
                gtk.idle_add(self._idle_select_minute)
            elif pos == 4:
                gtk.idle_add(self._idle_select_second)

    def button_pressed(self, entry, event):
        if event.type in [gtk.gdk._2BUTTON_PRESS, gtk.gdk._3BUTTON_PRESS]:
            entry.stop_emission('button-press-event')


    def button_released(self, entry, event):
        pos = entry.get_position()
        if 0 <= pos <= 2:
            gtk.idle_add(self._idle_select_hour)
        elif 3 <= pos <= 5:
            gtk.idle_add(self._idle_select_minute)
        elif 6 <= pos:
            gtk.idle_add(self._idle_select_second)

    def __init__(self,
                 entry, 
                 regexp = '^([0-1]\d?|2[0-3]?|):([0-5]\d?|):([0-5]\d?|)$',
                 initial = '00:00:00'):
        super(time_entry_control, self).__init__(entry, regexp, initial)
        entry.connect('changed', self.changed)
        entry.connect('button-press-event', self.button_pressed)
        entry.connect('button-release-event', self.button_released)
        self.set_time_format('%H:%M:%S')
        gtk.idle_add(self._idle_select_hour)

    def get_value(self):
        '''return time object if entry has valid time string
        return None elsewere
        \retval datetime.time
        \retval None if string did not parsed'''
        ret = None
        try:
            ret = datetime.strptime(self.entry.get_text(), self.get_time_format()).time()
        except ValueError:
            pass
        return ret
        

    def get_time_format(self):
        return self._time_format
    
    def set_time_format(self, value):
        self._time_format = value

    def set_value(self, value):
        if isinstance(value, basestring):
            try:
                self._emission_stopping = False
                t = datetime.strptime(value, self.get_time_format())
                self.entry.set_text(t.strftime(self.get_time_format()))
            except ValueError as e:
                self._emission_stopping = True
                print_error(e)
                raise e
            finally:
                self._emission_stopping = True
        elif isinstance(value, (time, datetime)):
            try:
                self._emission_stopping = False
                self.entry.set_text(value.strftime(self.get_time_format()))
            finally:
                self._emission_stopping = True
        else:
            raise od_exception_parameter_error('{0} is not a string or datetime value', value)
            

if __name__ == "__main__":
    win = gtk.Dialog()
    p = win.get_content_area()
    en = gtk.Entry()
    p.pack_start(en, False)
    x = time_entry_control(en)
    bt = gtk.Button('get value')
    lbl = gtk.Label()
    def time_to_string(dd):
        if isinstance(dd, (datetime, time)):
            return dd.isoformat()
        else:
            return 'None'

    def print_val(button):
        lbl.set_text(time_to_string(x.get_value()))
        
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
    def set_current_time(button):
        x.set_value(datetime.now())
    bt3 = gtk.Button('set current time')
    bt3.connect('clicked', set_current_time)
    p.pack_start(bt3)
    win.show_all()
    win.run()
    win.hide()