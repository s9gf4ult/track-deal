#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class status_bar_control:
    def __init__(self, global_data, database, builder):
        self.global_data = global_data
        self.database = database
        self.builder = builder
        def shorter(name):
            return self.builder.get_object(name)
        self.statusbar = shorter("main_statusbar")
        self.statusbar.set_homogeneous(False)
        self.db = gtk.Label()
        self.cacc = gtk.Label()
        self.deals = gtk.Label()
        self.poss = gtk.Label()
        self.has_unbalance = gtk.Label()
        for wid in [self.db, self.cacc, self.deals, self.poss]:
            self.statusbar.pack_start(wid, False)
        self.statusbar.pack_start(self.has_unbalance)
        self.statusbar.show_all()

    def update_widget(self):
        if self.database.connection == None:
            for lbl in [self.db, self.cacc, self.deals, self.poss, self.has_unbalance]:
                lbl.set_text("")
        else:
            self.db.set_text(self.database.filename == ":memory:" and u'База данных в памяти' or u'file: {0}'.format(self.database.filename))
            
            
