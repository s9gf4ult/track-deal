#!/bin/env python
# -*- coding: utf-8 -*-
## start_gtk ##


if __name__ == '__main__':
    import sqlite_model
    import gtk_view
    import sys
    import application
    import locale
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
    a = application.application(gtk_view.gtk_view())
    if len(sys.argv) > 1:
        m = sqlite_model.sqlite_model()
        m.open_existing(sys.argv[1])
        a.start(m)
    else:
        a.start()
