#!/bin/env python
# -*- coding: utf-8 -*-
from buffer_control import buffer_control

class date_buffer(buffer_control):

    def text_inserted(self, entry_buffer, position, chars, n_chars):
        return buffer_control.text_inserted(self, entry_buffer, position, chars, n_chars)


    def text_deleted(self, entry_buffer, position, n_chars):
        return buffer_control.text_deleted(self, entry_buffer, position, n_chars)