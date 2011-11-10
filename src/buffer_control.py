#!/bin/env python
# -*- coding: utf-8 -*-

class buffer_control(object):
    

    def text_inserted(self, entry_buffer, position, chars, n_chars):
        raise NotImplementedError()
    
    
    def text_deleted(self, entry_buffer, position, n_chars):
        raise NotImplementedError()
    
    
    def __init__(self, entry_buffer):
        self.entry_buffer = entry_buffer
        self.entry_buffer.connect('inserted-text', self.text_inserted)
        self.entry_buffer.connect('deleted-text', self.text_deleted)