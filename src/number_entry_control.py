#!/bin/env python
# -*- coding: utf-8 -*-
from regexp_entry_control import regexp_entry_control
from od_exceptions import od_exception_parameter_error


class number_entry_control(regexp_entry_control):
    def __init__(self, 
                 entry,
                 regexp = '^\d{1,}(.\d*)?$',
                 initial = '0'):
        super(number_entry_control, self).__init__(entry, regexp, initial)
        
    def get_value(self):
        return float(self.entry.get_text())
    
    def set_value(self, value):
        if isinstance(value, (int, float, long)):
            self.entry.set_text(str(value))
        elif isinstance(value, basestring):
            self.entry.set_text(value)
        else:
            raise od_exception_parameter_error('value must be string or number')
        
    
if __name__ == "__main__":
    import gtk
    win = gtk.Dialog()
    p = win.get_content_area()
    en = gtk.Entry()
    p.pack_start(en, False)
    x = number_entry_control(en)
    bt = gtk.Button('get value')
    lbl = gtk.Label()
    def date_to_string(dd):
        if isinstance(dd, (datetime, date)):
            return dd.isoformat()
        else:
            return 'None'

    def print_val(button):
        lbl.set_text(date_to_string(x.get_value()))
        
    bt.connect('clicked', print_val)
    p.pack_start(bt, False)
    p.pack_start(lbl, False)
    bt2 = gtk.Button('set value')
    en2 = gtk.Entry()
    p.pack_start(bt2, False)
    p.pack_start(en2, False)
    def set_val(button):
        x.set_value(en2.get_text())
    bt3 = gtk.Button('set current date')
    def set_current_date(button):
        x.set_value(datetime.now())
    bt3.connect('clicked', set_current_date)
    p.pack_start(bt3)
    bt2.connect('clicked', set_val)
    win.show_all()
    win.run()
    win.hide()