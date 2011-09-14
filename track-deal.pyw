#!/bin/env python
# -*- coding: utf-8 -*-
## start_gtk ##


if __name__ == '__main__':
    import sys
    import os
    scname = sys.argv[0]
    runpath = os.path.realpath(os.path.dirname(scname))
    sys.path.append(os.path.join(runpath, 'src'))      # if we are starting this from the project directory
    if os.name == 'posix':
        os.chdir(runpath)
    import sqlite_model
    import gtk_view
    import application
    import locale
    if os.name == 'posix':
        locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
    a = application.application(gtk_view.gtk_view())
    if len(sys.argv) > 1:
        a.start(sys.argv[1])
    else:
        a.start()
