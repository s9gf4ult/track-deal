#!/bin/env python
# -*- coding: utf-8 -*-
## gtk_view ##

import gtk
from common_view import common_view
from main_window_controller import main_window_controller
from sqlite_model import sqlite_model
from accounts_tab_controller import accounts_tab_controller
from account_edit_control import account_edit_control
from currency_edit_control import currency_edit_control
from deals_tab_controller import deals_tab_controller
from deal_adder_control import deal_adder_control
from deal_editor_control import deal_editor_control
from common_methods import *


class gtk_view(common_view):
    """
    \~russian
    Класс для рисования интерфейса на Gtk создает контролы и хранит их.
    \~english
    Open deals Gtk view class (gtk interface for open-deals)
    """
    ## \brief GtkBuilder instance.
    builder = None
    ## \brief \ref main_window_controller.main_window_controller instance.
    # \~russian
    # \par
    # Экземпляр контрола главного окна. Хранится сдесь для вызова метода обновления виджетов
    # которыми управляет контрол
    window = None
    ## \brief instance of implementor of \ref common_model.common_model
    model = None
    ## \brief instance of \ref currency_edit_control.currency_edit_control
    # \~russian
    # 
    # Экземпляр диалога для редактирования валют
    currency = None
    ## \brief instance of \ref accounts_tab_controller.accounts_tab_controller
    # Экземпляр контрола для таба со счетами. (Обработка событий нажатия кнопок и управление
    # списками на этой вкладке)
    accounts = None
    ## \brief instance of \ref account_edit_control.account_edit_control
    # \~russian \par Контрол формы редактирования счета
    account_edit = None
    ## \brief instance of \ref deals_tab_controller.deals_tab_controller
    deals_tab = None
    ## \brief instance of \ref deal_adder_control.deal_adder_control
    deal_adder = None
    ## \brief instance of \ref deal_editor_control.deal_editor_control
    deal_editor = None
    ## \brief \ref deals_filter.deals_filter instance
    deals_filter = None
    
    def __init__(self, ):
        """initialize gtk view
        \~russian
        """
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        self.currency = currency_edit_control(self)
        self.account_edit = account_edit_control(self)
        self.accounts = accounts_tab_controller(self)
        self.window = main_window_controller(self)
        self.deals_tab = deals_tab_controller(self)
        self.deal_adder = deal_adder_control(self)
        self.deal_editor = deal_editor_control(self)
        self.deals_filter = deals_filter(self)
    
    def run(self, ):
        """show main window and initialize all the necessary
        """
        self.window.run()
        gtk.main()
        
        
    def call_update_callback(self, ):
        """try send update signal to the all controllers
        """
        print("update !")
        self.window.update()
        self.accounts.update()
        self.deals_tab.update()

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
        self.model.open_existing(filename)

    def quit(self, ):
        """quit from gtk main loop
        """
        gtk.main_quit()
 
