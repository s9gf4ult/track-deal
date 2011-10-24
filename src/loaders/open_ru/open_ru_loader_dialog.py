#!/bin/env python
# -*- coding: utf-8 -*-
## open_ru_loader_dialog ##

import gtk, os
from combo_select_control import combo_select_control
from common_methods import show_error

class open_ru_loader_dialog(object):
    """\brief 
    """
    def __init__(self, parent):
        """\brief 
        \param parent - loader_dialog class instance
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
        self.account_control = combo_select_control(self.account)

    def run(self, ):
        """\brief run dialog, load data if necessary and hide window
        """
        if not self._parent._parent.connected():
            return
        self.prepare_dialog()
        self.window.show_all()
        ret = self.window.run()
        if ret == gtk.RESPONSE_ACCEPT:
            if not self.load_data():
                ret = gtk.RESPONSE_CANCEL
        self.window.hide()
        return ret

    def prepare_dialog(self, ):
        """\brief fill all necessary fields in dialog before show
        """
        model = self._parent._parent.get_model()
        self.account_control.update_answers([(ac['id'], ac['name']) for ac in model.list_accounts().fetchall()])
        if model.get_current_account() != None:
            self.account_control.set_value(model.get_current_account()['id'])

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
        account = self.account_control.get_value()
        if account == None:
            show_error(u'You need to select account to load data into', self.window)
            return False
        return True
