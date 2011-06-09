#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

import gtk
from main_window_controller import main_window_controller

class gtk_view(common_view):
    """Open deals Gtk view class (gtk interface for open-deals)
    """
    _builder = None
    _window = None
    _model = None
    
    def __init__(self, ):
        """initialize gtk view
        """
        self._builder = gtk.Builder()
        self._builder.add_from_file("main_ui.glade")
        self._window = main_window_controller(self)

    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        self._window.run()
        
        
    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        self._window.update()
