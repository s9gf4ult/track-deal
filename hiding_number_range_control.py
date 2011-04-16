#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import hide_control
from number_range_control import *

class hiding_number_range_control:
    def __init__(self, lower_spin, upper_spin, global_box = None, global_chbt = None, lower_chbt = None, upper_chbt = None):
        self.hiders = []
        
