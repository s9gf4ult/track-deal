#!/bin/env python
# -*- coding: utf-8 -*-

from open_ru_loader_dialog import open_ru_loader_dialog

def get_dialog_class():
    """
    \brief return the class representing dialog to run
    when importing the data from some stuff
    """
    return open_ru_loader_dialog

def get_icon_filename():
    """\brief return string with full path to icon
    """
    import os.path as path
    curpath = path.dirname(__file__)
    return path.join(curpath, 'icon.png')

def get_loader_name():
    """\brief return string with name of loader
    """
    return u'Отчет брокера "Открытие"'

