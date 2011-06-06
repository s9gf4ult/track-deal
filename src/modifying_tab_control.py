#!/bin/env python
# -*- coding: utf-8 -*-

class modifying_tab_control:

    def call_update_callback(self):
        if self.update_callback:
            self.update_callback()
        else:
            self.update_widget()

        
        
    
