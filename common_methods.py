#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

def show_error(message, parent):
    win = parent
    dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
    dial.props.text = message
    dial.run()
    dial.destroy()

def find_in_list(findfunc, flist):
    for x in xrange(0, len(flist)):
        if findfunc(flist[x]):
            return x
    return None
