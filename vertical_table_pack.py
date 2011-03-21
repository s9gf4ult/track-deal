#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

def pack_vertical(rows_list, expandingrow = None, expandingcol = None):
    rows = len(rows_list)
    cols = max(map(lambda a: len(a), rows_list))
    t = gtk.Table(rows = rows, columns = cols)
    for rid in xrange(0, len(rows_list)):
        for cid in xrange(0, len(rows_list[rid])):
            t.attach(rows_list[rid][cid], left_attach = cid, right_attach = cid + 1, top_attach = rid, bottom_attach = rid + 1, xoptions = expandingcol and cid == expandingcol and gtk.FILL | gtk.EXPAND or gtk.FILL, yoptions = expandingrow and rid == expandingrow and gtk.FILL | gtk.EXPAND or gtk.FILL)

    return t

if __name__ == "__main__":
    w = gtk.Dialog(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    w.get_content_area().pack_start(pack_vertical([(gtk.Label("eijfiejf"), gtk.Label("iji")), (gtk.Label("ijij"),)], expandingcol = 1, expandingrow = 1))
    w.show_all()
    w.run()
