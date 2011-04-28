#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from math import *
import traceback



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

def is_null_or_empty(obj):
    return obj == None or len(obj) == 0

def reduce_by_string(reductor, seq):
    return reduce(lambda a, b: u'{0}{1}{2}'.format(a, reductor, b),
                  seq)

def seconds_to_time_distance(seconds):
    ret = {}
    for (key, mlt) in [("days", 24 * 3600),
                       ("hours", 3600),
                       ("minutes", 60),
                       ("seconds", 1)]:
        ret[key] = trunc(seconds / mlt)
        seconds = seconds % mlt
    return ret

def time_distance_to_seconds(tdist):
    ret = reduce(lambda a, b: a + b,
                 map(lambda x, y: x * y,
                     [24 * 3600, 3600, 60, 1],
                     map(lambda k: gethash(tdist, k) != None and tdist[k] or 0,
                         ["days", "hours", "minutes", "seconds"])))
    return ret

def solve_lower_upper(plus, conds, field_name, l, h):
    if l and h:
        if l < h:
            conds.append(u'({0} between ? and ?)'.format(field_name))
            plus += [l, h]
        elif l > h:
            conds.append(u'({0} >= ? or {0} <= ?)'.format(field_name))
            plus += [l, h]
        else:
            conds.append(u'{0} = ?'.format(field_name))
            plus.append(l)
    elif l:
        conds.append(u'{0} >= ?'.format(field_name))
        plus.append(l)
    elif h:
        conds.append(u'{0} <= ?'.format(field_name))
        plus.append(h)

def show_and_print_error(error, window):
    show_error(error.__str__(), window)
    print(traceback.format_exc())

def no_reaction(func):
    """decorator which blocks an execution of the method of object which has `react` member, if react is False methid will not executed, before execution of the method `react` sets to False"""
    def ret(*args, **kargs):
        if not args[0].__do_react__:
            return
        try:
            args[0].__do_react__ = False
            func(*args, **kargs)
        finally:
            args[0].__do_react__ = True
    return ret
