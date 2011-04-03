#!/bin/env python
# -*- coding: utf-8 -*-
from datetime_control import *
from combo_control import *
from number_range_control import number_control
from time_control import *
from select_control import *

class deal_adder_control:
    def __init__(self, builder):
        self.builder = builder
        def shorter(name):
            return self.builder.get_object("deal_adder_{0}".format(name))
        
        self.datetime = datetime_control(shorter("calendar"))
                                         time_control(shorter("hour"),
                                                      shorter("min"),
                                                      shorter("sec")))
        self.instrument = combo_control(shorter("stock"))
        self.market = combo_control(shorter("market"))
        self.price = number_control(shorter("price"))
        self.count = number_control(shorter("count"))
        self.direction = select_control({ -1 : shorter("buy_rb"),
                                          1 : shorter("sell_rb")})
        self.broker_comm = number_control(shorter("broker_comm"))
        self.stock_comm = number_control(shorter("stock_comm"))

    def get_
