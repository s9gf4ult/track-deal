#!/bin/env python
# -*- coding: utf-8 -*-

from common_methods import print_error
from datetime import date, datetime, MINYEAR, MAXYEAR
from od_exceptions import od_exception_parameter_error
from regexp_entry_control import regexp_entry_control
import gtk
import re

class date_entry_control(regexp_entry_control):
    
    def _idle_select_year(self):
        self.entry.select_region(0, 4)
        
    def _idle_select_month(self):
        self.entry.select_region(5, 7)
        
    def _idle_select_day(self):
        self.entry.select_region(8, -1)

    def changed(self, entry):
        if re.match('^\d{4}-\d{2}-\d{2}', entry.get_text()):
            pos = entry.get_position()
            if pos == 3:
                gtk.idle_add(self._idle_select_month)
            elif pos == 6:
                gtk.idle_add(self._idle_select_day)
    

    def released(self, entry, event):
        if re.match('^\d{4}-\d{2}-\d{2}$', entry.get_text()):
            pos = entry.get_position()
            if 0 <= pos <= 4:
                gtk.idle_add(self._idle_select_year)
            elif 5 <= pos <= 7:
                gtk.idle_add(self._idle_select_month)
            elif 8 <= pos:
                gtk.idle_add(self._idle_select_day)

    def pressed(self, entry, event):
        if event.type in [gtk.gdk._2BUTTON_PRESS, gtk.gdk._3BUTTON_PRESS]:
            entry.stop_emission('button-press-event')
    

    def set_date_format(self, value):
        self._date_format = value
        
    def get_date_format(self):
        return self._date_format
    
    def __init__(self, entry, 
                 regexp = '^\d{0,4}-(0\d?|1[0-2]?|)-(0[1-9]?|[1-2]\d?|3[0-1]?|)$', 
                 initial = '0001-01-01'):
        super(date_entry_control, self).__init__(entry, regexp, initial)
        entry.connect('changed', self.changed)
        entry.connect('button-release-event', self.released)
        entry.connect('button-press-event', self.pressed)
        self.set_date_format('%Y-%m-%d')
        gtk.idle_add(self._idle_select_year)

    def post_match_hook(self, entry, new_text):
        mobj = re.search('^(\d{4})-(\d{2})-(\d{2})$', new_text)
        if mobj != None:
            ret = True
            (year, month, day) = mobj.group(1, 2, 3) 
            if not (MINYEAR <= int(year) <= MAXYEAR):
                ret = False
            if not (1 <= int(month) <= 12):
                ret =  False
            try:
                date(int(year), int(month), int(day))
            except:
                ret = False
            return ret
        return True
    
    def get_value(self):
        '''return datetime entered into the entry
        '''
        dtext = self.entry.get_text()
        val = None
        try:
            val = datetime.strptime(dtext, self.get_date_format()).date()
        except ValueError:
            pass
        return val
    
    def set_value(self, dtm):
        if isinstance(dtm, basestring):
            try:
                self._emission_stopping = False # this is stupid
                dd = datetime.strptime(dtm, self.get_date_format())
                self.entry.set_text(dd.strftime(self.get_date_format()))
            except ValueError as e:
                self._emission_stopping = True
                print_error(e)
                raise e
            finally:
                self._emission_stopping = True
        elif isinstance(dtm, (date, datetime)):
            try:
                self._emission_stopping = False
                self.entry.set_text(dtm.strftime(self.get_date_format()))
            finally:
                self._emission_stopping = True
        else:
            raise od_exception_parameter_error('{0} is not a string or datetime object'.format(dtm))
            
                    
         
        
if __name__ == "__main__":
    win = gtk.Dialog()
    p = win.get_content_area()
    en = gtk.Entry()
    p.pack_start(en, False)
    x = date_entry_control(en)
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