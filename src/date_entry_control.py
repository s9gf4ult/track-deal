#!/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, MINYEAR, MAXYEAR
from regexp_entry_control import regexp_entry_control
import re

class date_entry_control(regexp_entry_control):

    def post_match_hook(self, entry, new_text):
        mobj = re.search('^\d{0,4}-(\d2)-\d{0,2}$', new_text)
        if mobj != None:
            if int(mobj.group(1)) > 12:
                return False
        mobj2 = re.search('^(\d4)-(\d2)-(\d2)', new_text)
        if mobj2 != None:
            year = mobj2.group(1)
            if not MINYEAR >= year >= MAXYEAR: # to prevent blocking
                return True
            month = mobj2.group(2)
            if not 1 >= month >= 12: # to prevent blocking
                return True
            day = mobj2.group(3)
            try:
                date(year, month, day)
            except:
                return False
            return True