#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control

class accounts_tab_controller(modifying_tab_control):
    def __init__(self, database, builder, update_callback):
        self.builder = builder
        self.database = database
        self.update_callback = update_callback

        
    
