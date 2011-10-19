#!/bin/env python
# -*- coding: utf-8 -*-
## open_ru_loader_dialog ##

import gtk, os

class open_ru_loader_dialog(object):
    """\brief 
    """
    def __init__(self, parent):
        """\brief 
        \param parent
        """
        self._parent = parent
        self.builder = gtk.Builder()
        dialogpath = os.path.join(os.path.dirname(__file__), 'dialog.glade')
        self.builder.add_from_file(dialogpath)
        self.window = self.builder.get_object('dialog')
        self.window.add_buttons(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        if os.name == 'posix':
            fltr = gtk.FileFilter()
            fltr.set_name(u'Отчет из "Открытия"')
            fltr.add_mime_type('application/xml')
            self.window.add_filter(fltr)
        elif os.name == 'nt':   # windows can not mime types
            fltr = gtk.FileFilter()
            fltr.set_name(u'Отчет из "Открытия"')
            fltr.add_pattern('*.xml')
            self.window.add_filter(fltr)
        self.repo = self.builder.get_object('load_repo')
        self.accounts = self.builder.get_object('load_accounts')
        self.account = self.builder.get_object('account')

    def run(self, ):
        """\brief run dialog, load data if necessary and hide window
        """
        self.window.show_all()
        ret = self.window.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self.load_data()
        self.window.hide()
        return ret

    def destroy(self, ):
        """\brief destroy dialog
        """
        self.window.destroy()
        self.window = None
        self.repo = None
        self.accounts = None
        self.account = None
        self.builder = None

    def load_data(self, ):
        """\brief load data into selected account
        """
        return None
