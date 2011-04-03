#!/bin/env python
# -*- coding: utf-8 -*-
from datetime_control import *
from combo_control import *
from number_range_control import number_control
from time_control import *

class deal_adder_control:
    def __init__(self, builder):
        self.builder = builder
        self.datetime = datetime_control(self.builder.get_object("deal_adder_calendar"),
                                         time_control(self.builder.get_object("deal_adder_hour"),
                                                      self.builder.get_object("deal_adder_min"),
                                                      self.builder.get_object("deal_adder_sec")))
        
