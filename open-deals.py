#!/bin/env python
# -*- coding: utf-8 -*-
## start_gtk ##


if __name__ == '__main__':
    import sys
    sys.path.append('src')      # if we are starting this from the project directory
    import os
    import sqlite_model
    import gtk_view
    import application
    import locale
    if os.name == 'posix':
        locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
    a = application.application(gtk_view.gtk_view())
    if len(sys.argv) > 1:
        m = sqlite_model.sqlite_model()
        m.open_existing(sys.argv[1])
        a.start(m)
    else:
        a.start()
