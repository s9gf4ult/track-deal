#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

from main_window_controller import main_window_controller


class gtk_view(common_view):
    """Open deals Gtk view class (gtk interface for open-deals)
    """
    def __init__(self, ):
        """initialize gtk view
        """
        self._window = main_window_controller()

    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        pass

    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        self._window.update()
