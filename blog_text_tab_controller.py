#!/bin/env python
# -*- coding: utf-8 -*-

class blog_text_tab_controller:
    def __init__(self, database, builder):
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)

        self.database = database
        self.builder = builder
        shorter("stock_view", "cursor-changed", self.stock_cursor_changed)
        shorter("date_view", "cursor-changed", self.date_cursor_changed)
        
