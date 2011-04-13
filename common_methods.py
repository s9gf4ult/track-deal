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

def gethash(fhash, key):
    if fhash.has_key(key):
        return fhash[key]
    else:
        return None

def find_in_model(tmodel, findfunc):
    """returns path of found row in model"""
    it = tmodel.get_iter_first()
    while it != None:
        if findfunc(tmodel, it):
            return it
        it = tmodel.iter_next(it)
    return None
