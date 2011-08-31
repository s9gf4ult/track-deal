#!/bin/env python
# -*- coding: utf-8 -*-
## settings_dialog_controller ##
from common_methods import make_builder
import gtk
import sys
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
        self.legend_top = shobject('legend_top')
        self.legend_bottom = shobject('legend_bottom')
        self.legend_font = shobject('legend_font')
        self.legend_color = shobject('legend_color')
        self.line_width = shobject('line_width')
        self.line_color = shobject('line_color')
        self.mesh_font = shobject('mesh_font')
        self.mesh_font_color = shobject('mesh_font_color')
        self.back_ground_color = shobject('background_color')
        self.line_width.set_digits(2)
        self.line_width.get_adjustment().set_all(lower = 0, upper = sys.maxint, step_increment = 0.1, page_increment = 1)
        
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
        for key, value in [('interface.odd_color', self.odd_color.get_color().to_string()),
                           ('interface.even_color', self.even_color.get_color().to_string()),
                           ('behavior.load_last_database', self.load_last_database.get_active()),
                           ('chart.legend.position', ('bottom' if self.legend_bottom.get_active() else 'top')),
                           ('chart.legend.font', self.legend_font.get_font_name()),
                           ('chart.legend.color', self.legend_color.get_color().to_string()),
                           ('chart.mesh.line_width', self.line_width.get_value()),
                           ('chart.mesh.color', self.line_color.get_color().to_string()),
                           ('chart.mesh.font.name', self.mesh_font.get_font_name()),
                           ('chart.mesh.font.color', self.mesh_font_color.get_color().to_string()),
                           ('chart.background.color', self.back_ground_color.get_color().to_string())]:
            self._parent.settings.set_key(key, value)

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

        try:
            legpos = self._parent.settings.get_key('chart.legend.position')
            if legpos == 'top':
                self.legend_top.set_active(True)
            else:
                self.legend_bottom.set_active(True)
        except od_exception_config_key_error:
            self.legend_bottom.set_active(True)

        try:
            self.legend_font.set_font_name(self._parent.settings.get_key('chart.legend.font'))
        except od_exception_config_key_error:
            pass

        try:
            self.legend_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('chart.legend.color')))
        except od_exception_config_key_error:
            self.legend_color.set_color(gtk.gdk.Color('#FFFFFF'))

        try:
            self.line_width.set_value(self._parent.settings.get_key('chart.mesh.line_width'))
        except od_exception_config_key_error:
            self.line_width.set_value(1.5)

        try:
            self.line_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('chart.mesh.color')))
        except od_exception_config_key_error:
            self.line_color.set_color(gtk.gdk.Color('#FFFFFF'))

        try:
            self.mesh_font.set_font_name(self._parent.settings.get_key('chart.mesh.font.name'))
        except od_exception_config_key_error:
            pass

        try:
            self.mesh_font_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('chart.mesh.font.color')))
        except od_exception_config_key_error:
            self.mesh_font_color.set_color(gtk.gdk.Color('#FFFFFF'))

        try:
            self.back_ground_color.set_color(gtk.gdk.Color(self._parent.settings.get_key('chart.background.color')))
        except od_exception_config_key_error:
            self.back_ground_color.set_color(gtk.gdk.Color('#000000'))
