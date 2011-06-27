#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

import gtk
from common_view import common_view
from main_window_controller import main_window_controller
from sqlite_model import sqlite_model
from accounts_tab_controller import accounts_tab_controller

class gtk_view(common_view):
    """
    \if russian
    Класс для рисования интерфейса на Gtk создает контролы и хранит их.
    \else
    Open deals Gtk view class (gtk interface for open-deals)
    \endif
    """
    ## \brief GtkBuilder instance
    builder = None
    window = None
    model = None
    
    def __init__(self, ):
        """initialize gtk view
        """
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        self.window = main_window_controller(self)
        self._accounts = accounts_tab_controller(self)

    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        self.window.run()
        gtk.main()
        
        
    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        self.window.update()
        self._accounts.update()

    def connected(self, ):
        """\retval True if model exist and connected
        """
        return self.model <> None and self.model.connected()

    def disconnect(self, ):
        """
        \retval True if disconnected successfully
        \retval False if did not disconnected
        """
        if self.connected():
            try:
                self.model.disconnect()
                self.model = None
            except Exception as e:
                show_error(e.__str__(), self.builder.get_object("main_window"))
                print(traceback.format_exc())
                return False
            else:
                return True
        else:
            return True

    def create_new_sqlite(self, filename):
        """connect to new sqlite model and create new database in it
        \param filename file to create database in
        """
        self.model = sqlite_model()
        self.model.create_new(filename)

    def open_existing_sqlite(self, filename):
        """connect to existing sqlite file
        \param filename 
        """
        self.model = sqlite_model()
        self.model.open_existing(filename)

    def quit(self, ):
        """quit from gtk main loop
        """
        gtk.main_quit()
