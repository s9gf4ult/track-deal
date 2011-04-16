#!/bin/env python
# -*- coding: utf-8 -*-

from hide_control import *
from select_control import *

class hiding_select_control(select_control):
    def __init__(self, answers, checkbutton = None, box = None):
        if checkbutton != None and box != None:
            self.hiders = [hide_control(checkbutton, box)]
        select_control.__init__(self, answers, checkbutton)
                           
