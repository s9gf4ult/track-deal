#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class account_edit_control:
    def __init__(self, builder):
        self.builder = builder
        def shobject(name):
            return self.builder.get_object(name)
        self.window = shobject("account_edit")
        self.window.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
