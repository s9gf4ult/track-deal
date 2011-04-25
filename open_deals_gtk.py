#!/bin/env python
# -*- coding: utf-8 -*-
import sources
import deals_core
import gtk
import traceback
from deals_filter import deals_filter
from deal_adder_control import deal_adder_control
from deals_tab_controller import deals_tab_controller
from report_tab_control import report_tab_control
from blog_text_tab_controller import blog_text_tab_controller
from main_window_controller import main_window_controller
from positions_tab_controller import positions_tab_controller
from accounts_tab_controller import accounts_tab_controller
from account_edit_control import account_edit_control
from deal_editor_control import deal_editor_control
from report_importer_control import report_importer_control
from positions_filter import *

class main_ui():

    def __init__(self):
        self.database = deals_core.deals_proc()
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        self.global_data = {}
        
        # main window
        self.main_window = main_window_controller(self.database, self.builder, self.update_view)

        # report tab
        self.report_tab = report_tab_control(self.database, self.builder)

        # blog tab
        self.blog_tab = blog_text_tab_controller(self.database, self.builder)

        # deals tab
        self.deals_filter = deals_filter(self.global_data, self.builder, self.database)
        self.deal_adder = deal_adder_control(self.builder)
        self.deal_editor = deal_editor_control(self.builder)
        self.report_importer = report_importer_control(self.builder)
        self.deals_tab = deals_tab_controller(self.global_data, self.database, self.builder, self.update_view, self.deals_filter, self.deal_adder, self.deal_editor, self.report_importer)
        # positions tab
        self.pfilter = positions_filter(self.global_data, self.builder, self.database)
        self.positions_tab = positions_tab_controller(self.database, self.builder, self.pfilter, self.update_view)

        # accounts tab
        self.account_edit = account_edit_control(self.builder)
        self.accounts_tab = accounts_tab_controller(self.global_data, self.database, self.builder, self.update_view, self.account_edit)
        self.update_view()
        
    def show(self):
        win = self.builder.get_object("main_window")
        win.show_all()

    def update_view(self):
        self.accounts_tab.update_widget()
        self.deals_tab.update_widget()
        self.report_tab.update_widget()
        self.blog_tab.update_widget()
        self.main_window.update_widget()
        
if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
