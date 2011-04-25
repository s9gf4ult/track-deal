#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control

class positions_tab_controller(modifying_tab_control):
    def __init__(self, database, builder, pfilter, update_callback):
        self.database = database
        self.builder = builder
        self.pfilter = pfilter
        self.update_callback = update_callback
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)

        shorter("positions_make", "activate", self.make_positions_activate)
        shorter("call_positions_filter", "activate", self.filter_activate)

    def make_positions_activate(self, action):
        self.make_positions()

    def make_positions(self):
        if self.database.connection:
            self.database.make_positions()
            self.call_update_callback()
    
    def filter_activate(self, action):
        self.pfilter.run()
