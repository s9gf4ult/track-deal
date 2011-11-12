#!/bin/env python
# -*- coding: utf-8 -*-

from od_exceptions import od_exception_parameter_error
import re

class regexp_entry_control(object):

    def get_regexp(self):
        return self.regexp
    
    def set_regexp(self, regexp):
        self.regexp = regexp
    
    def post_match_hook(self, entry, new_text):
        '''return True if given text can be processed
        '''
        return True
    
    def stop_emission(self, entry, new_text, signal_name):
        if not self._emission_stopping:
            return
        expression = re.compile(self.get_regexp())
        if not (expression.match(new_text) and self.post_match_hook(entry, new_text)): 
            entry.stop_emission(signal_name)

    def text_deleted(self, entry, start, end):
        x = entry.get_text()
        self.stop_emission(entry, x[:start] + x[end:], 'delete-text')
    
    def text_inserted(self, entry, new_text, new_text_length, position):
        x = entry.get_text()
        pos = entry.get_position()
        self.stop_emission(entry, x[:pos] + new_text + x[pos:], 'insert-text')

    def __init__(self, entry, regexp = '^\d{0,4}-\d{0,2}-\d{0,2}$', initial = '0001-01-01'):
        if not re.match(regexp, initial):
            raise od_exception_parameter_error('value {0} does not match regexp {1}'.format(initial, regexp))
        self._emission_stopping = True
        self.entry = entry
        self.set_regexp(regexp)
        self.entry.set_text(initial)
        self.entry.connect('delete-text', self.text_deleted)
        self.entry.connect('insert-text', self.text_inserted)
        