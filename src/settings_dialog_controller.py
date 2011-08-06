#!/bin/env python
# -*- coding: utf-8 -*-
## settings_dialog_controller ##
from common_methods import make_builder
import gtk
from od_exceptions import od_exception_config_key_error

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
        self.odd_color = shobject('odd_color')
        self.even_color = shobject('even_color')
        self.load_last_database = shobject('load_last_database')

    def run(self, ):
        """\brief run dialog and save settings if SAVE pressed
        \retval gtk.RESPONSE_ACCEPT
        \retval gtk.RESPONSE_CANCEL
        """
        self.load_settings()
        ret = self.window.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self.save_settings()
        self.window.hide()
        return ret

    def save_settings(self, ):
        """\brief save setting into settings instance
        """
        self._parent.settings.set_key('interface.odd_color', self.odd_color.get_color().to_string())
        self._parent.settings.set_key('interface.even_color', self.even_color.get_color().to_string())
        self._parent.settings.set_key('behavior.load_last_database', self.load_last_database.get_active())

    def load_settings(self, ):
        """\brief load settings from settings instance into dialog
        """
        try:
            self.odd_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('interface.odd_color')))
        except od_exception_config_key_error:
            self.odd_color.set_color(gtk.gdk.Color('#FFFFFF'))

        try:
            self.even_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('interface.even_color')))
        except od_exception_config_key_error:
            self.even_color.set_color(gtk.gdk.Color('#FFFFFF'))

        try:
            self.load_last_database.set_active(self._parent.settings.get_key('behavior.load_last_database'))
        except od_exception_config_key_error:
            self.load_last_database.set_active(True)
                                      
