#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

import gtk
from common_view import common_view
from main_window_controller import main_window_controller
from sqlite_model import sqlite_model
from accounts_tab_controller import accounts_tab_controller

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
        self._accounts = accounts_tab_controller(self)

    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        self._window.run()
        gtk.main()
        
        
    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        self._window.update()
        self._accounts.update()

    def connected(self, ):
        """return true if model exist and connected
        """
        return self._model <> None and self._model.connected()

    def disconnect(self, ):
        """return true if disconnected successfully
        """
        if self.connected():
            try:
                self._model.disconnect()
                self._model = None
            except Exception as e:
                show_error(e.__str__(), self._builder.get_object("main_window"))
                print(traceback.format_exc())
                return False
            else:
                return True
        else:
            return True

    def create_new_sqlite(self, filename):
        """connect to new sqlite model and create new database in it
        Arguments:
        - `filename`:
        """
        self._model = sqlite_model()
        self._model.create_new(filename)

    def open_existing_sqlite(self, filename):
        """connect to existing sqlite file
        Arguments:
        - `filename`:
        """
        self._model = sqlite_model()
        self._model.open_existing(filename)

    def quit(self, ):
        """quit from gtk main loop
        """
        gtk.main_quit()
