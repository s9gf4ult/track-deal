#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from common_methods import *

class status_bar_control:
    def __init__(self, global_data, database, builder):
        self.global_data = global_data
        self.database = database
        self.builder = builder
        def shorter(name):
            return self.builder.get_object(name)
        self.db = shorter("main_status_db")
        self.cacc = shorter("main_status_cacc")
        self.deals = shorter("main_status_deals")
        self.poss = shorter("main_status_poss")
        self.unbal = shorter("main_status_unbal")
        self.changes = shorter("main_status_changes")

    def update_widget(self):
        if self.database.connection == None:
            for sb in [self.db, self.cacc, self.deals, self.poss, self.unbal]:
                sb.set_text("")
        else:
            self.db.set_text(self.database.filename == ":memory:" and u'База данных в памяти' or u'file: {0}'.format(self.database.filename))
            self.changes.set_text(u'Несохраннных изменений {0}'.format(self.database.get_changes()))

            if gethash(self.global_data, "current_account") != None:
                for (lbl, text) in [(self.cacc, u'Счет: {0}'.format(self.database.get_account_name_by_id(self.global_data["current_account"]))),
                                    (self.deals, u'Сделок: {0}'.format(self.database.get_count_deals_in_account(self.global_data["current_account"]))),
                                    (self.poss, u'Позиций: {0}'.format(self.database.get_count_positions_in_account(self.global_data["current_account"])))]:
                    lbl.set_text(text)
            else:
                for t in [self.cacc, self.deals, self.poss, self.unbal]:
                    t.set_text("")
            
            
