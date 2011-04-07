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

class main_ui():

    def quit(self, wid):
        try:
            self.database.close()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())
            return True
        gtk.main_quit()
        return False

    def window_quit(self, wid, evt):
        return self.quit(wid)
        
    def create_in_memory(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection:
            self.database.create_new(":memory:")
            self.update_view()

    def create_in_file(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection:
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Новая база', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self.database.create_new(diag.get_filename())
                    self.update_view()
                except Exception as e:
                    self.show_error(e.__str__())
                    print(traceback.format_exc())
            diag.destroy()

    def open_existing(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection: # это значит если база закрылась
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Открыть базу', parent = win, action = gtk.FILE_CHOOSER_ACTION_OPEN)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            fl = gtk.FileFilter()
            fl.add_mime_type('application/x-sqlite3')
            diag.set_filter(fl)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self.database.open_existing(diag.get_filename())
                    self.update_view()
                except Exception as e:
                    self.show_error(e.__str__())
                    print(traceback.format_exc())
            diag.destroy()
            fl.destroy()
            
    def close(self, wid):
        try:
            self.database.close()
            self.update_view()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())

    def commit(self, wid):
        if self.database.connection:
            self.database.commit()

    def rollback(self, wid):
        if self.database.connection:
            self.database.rollback()
            self.update_view()


    def check_if_database_open(self):
        if self.database.connection:
            return True
        else:
            self.show_error(u'Необходимо открыть или создать новую базу данных')
            return False

    def make_positions(self, wid):
        if self.check_if_database_open():
            self.database.make_positions()
            self.update_view()

    def __init__(self):
        self.database = deals_core.deals_proc()
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        # self.builder.connect_signals({"on_main_window_delete_event" : self.window_quit,
        #                               "on_create_database_in_memory_activate" : self.create_in_memory,
        #                               "on_create_database_activate" : self.create_in_file,
        #                               "on_open_database_activate" : self.open_existing,
        #                               "on_close_database_activate" : self.close,
        #                               "on_transaction_commit_activate" : self.commit,
        #                               "on_transaction_rollback_activate" : self.rollback,
        #                               "on_positions_make_activate" : self.make_positions,
        #                               "on_quit_activate" : self.quit})
        self.main_window = main_window_controller(self.database, self.builder, self.update_view)

        # report tab
        self.report_tab = report_tab_control(self.database, self.builder)

        # blog tab
        self.blog_tab = blog_text_tab_controller(self.database, self.builder)

        # deals tab
        self.deals_filter = deals_filter(self.builder, self.database)
        self.deal_adder = deal_adder_control(self.builder)
        self.deals_tab = deals_tab_controller(self.database, self.builder, self.update_view, self.deals_filter, self.deal_adder)
        
    def show_error(self, text):
        win = self.builder.get_object("main_window")
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
        dial.props.text = text
        dial.run()
        dial.destroy()
        
    def update_view(self):
        self.deals_tab.update_widget()
        self.report_tab.update_widget()
        self.blog_tab.update_widget()
        self.main_window.update_widget()

    def show(self):
        win = self.builder.get_object("main_window")
        win.show_all()

        
if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
