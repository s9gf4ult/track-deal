#!/bin/env python
# -*- coding: utf-8 -*-

class datetime_start_end_control:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.start.update_callback = self.start_changed
        self.end.update_callback = self.end_changed

    def start_changed(self):
        s = self.start.get_datetime()
        e = self.end.get_datetime()
        if s > e:
            self.end.set_datetime(s)

    def end_changed(self):
        s = self.start.get_datetime()
        e = self.end.get_datetime()
        if e < s:
            self.start.set_datetime(e)

    
