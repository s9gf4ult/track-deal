#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

import gtk
import sqlite3
from common_view import common_view
from main_window_controller import main_window_controller
from sqlite_model import sqlite_model
from accounts_tab_controller import accounts_tab_controller
from account_edit_control import account_edit_control
from currency_edit_control import currency_edit_control
from deals_tab_controller import deals_tab_controller
from deal_adder_control import deal_adder_control
from deal_editor_control import deal_editor_control
from deals_filter import deals_filter
from paper_adder import paper_adder
from positions_tab_controller import positions_tab_controller
from positions_filter import positions_filter
from position_adder_control import position_adder_control
from points_control import points_control
from report_importer_control import report_importer_control
from chart_tab_controller import chart_tab_controller
from common_methods import show_and_print_error, is_null_or_empty
from od_settings import settings
from settings_dialog_controller import settings_dialog_controller
import os
from account_in_out_controller import account_in_out_controller

class gtk_view(common_view):
    """
    \~russian
    Класс для рисования интерфейса на Gtk создает контролы и хранит их.
    \~english
    Track Deals Gtk view class (gtk interface for track-deals)
    """
    def __init__(self, ):
        """initialize gtk view
        """
        self.model = None
        self.settings = settings()
        self.window = main_window_controller(self)
        if self.settings.get_key('behavior.load_last_database'):
            dbpath = self.settings.get_key('database.path')
            if not (is_null_or_empty(dbpath) or dbpath == ':memory:'):
                try:
                    self.open_existing_sqlite(dbpath)
                except sqlite3.OperationalError as e:
                    show_and_print_error(e, self.window.builder.get_object('main_window'))
            else:
                self.settings.set_key('database.path', '')
        self.currency = currency_edit_control(self)
        self.account_edit = account_edit_control(self)
        self.accounts = accounts_tab_controller(self)
        self.deals_tab = deals_tab_controller(self)
        self.deal_adder = deal_adder_control(self)
        self.deal_editor = deal_editor_control(self)
        self.deals_filter = deals_filter(self)
        self.paper_adder = paper_adder(self)
        self.positions_tab = positions_tab_controller(self)
        self.positions_filter = positions_filter(self)
        self.position_adder = position_adder_control(self)
        self.points = points_control(self)
        self.report_importer = report_importer_control(self)
        self.chart_tab = chart_tab_controller(self)
        self.settings_dialog = settings_dialog_controller(self)
        self.account_in_out = account_in_out_controller(self)
        self.call_update_callback()
        
    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        self.window.run()
        gtk.main()
        
    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        self.window.update()
        self.accounts.update()
        self.deals_tab.update()
        self.positions_tab.update()
        self.chart_tab.update()

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
                show_and_print_error(e, self.window.builder.get_object("main_window"))
                return False
            else:
                return True
        else:
            return True

    def create_new_sqlite(self, filename):
        """connect to new sqlite model and create new database in it
        \param filename file to create database in
        """
        if self.connected():
            if not self.disconnect():
                return
        self.model = sqlite_model()
        self.model.create_new(filename)

    def open_existing_sqlite(self, filename):
        """connect to existing sqlite file
        \param filename 
        """
        if self.connected():
            if not self.disconnect():
                return
        self.model = sqlite_model()
        if os.path.exists(filename):
            self.model.open_existing(filename)

    def quit(self, ):
        """quit from gtk main loop
        """
        self.settings.save_config()
        gtk.main_quit()




