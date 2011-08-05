#!/bin/env python
# -*- coding: utf-8 -*-
## settings_dialog_controller ##
from common_methods import make_builder
import gtk

class settings_dialog_controller(object):
    """\brief controller for settings dialog
    """
    def __init__(self, parent):
        """\brief
        \param parent - \ref gtk_view.gtk_view instance
        """
        self._parent = parent
        self.builder = make_builder('glade/settings_dialog.glade')
        def shobject(name):
            return self.builder.get_object(name)

        self.window = shobject('settings_dialog')
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.window.set_transient_for(self._parent.window.builder.get_object('main_window'))
        self.load_settings()

    def run(self, ):
        """\brief run dialog and save settings if SAVE pressed
        \retval gtk.RESPONSE_ACCEPT
        \retval gtk.RESPONSE_CANCEL
        """
        ret = self.window.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self.save_settings()
        return ret

    def save_settings(self, ):
        """\brief save setting into settings instance
        """
        raise NotImplementedError()

    def load_settings(self, ):
        """\brief load settings from settings instance into dialog
        """
        raise NotImplementedError()
