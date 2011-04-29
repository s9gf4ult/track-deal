#!/bin/env python
# -*- coding: utf-8 -*-
import traceback
import shutil
import gtk
from modifying_tab_control import modifying_tab_control
from common_methods import *

class main_window_controller(modifying_tab_control):
    def __init__(self, global_data, database, builder, update_callback):
        self.database = database
        self.builder = builder
        self.global_data = global_data
        self.update_callback = update_callback
        def shorter(name, signal, *method):
            self.builder.get_object(name).connect(signal, *method)

        shorter("quit", "activate", self.quit_activate)
        shorter("create_database", "activate", self.create_database_activate)
        shorter("open_database", "activate", self.open_database_activate)
        shorter("transaction_commit", "activate", self.transaction_commit_activate)
        shorter("transaction_rollback", "activate", self.transaction_rollback_activate)
        shorter("close_database", "activate", self.close_activate)
        shorter("create_database_in_memory", "activate", self.create_database_in_memory_activate)
        shorter("main_window", "delete-event", self.main_window_quit)
        shorter("import_from_old_database", "activate", self.import_from_old_database_activate)
        shorter("save_as", "activate", self.save_as_activate)

    def save_as_activate(self, action):
        self.save_as()

    def save_as(self):
        if self.database.connection == None:
            return
        win = self.builder.get_object("main_window")
        ch = self.database.get_changes()
        if ch > 0:
            show_error(u'Перед сохранением нужно завершить транзакцию выполните Rollback или Commit', win)
            return
        dial = gtk.FileChooserDialog(title = u'Сохранить как', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE, buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        if dial.run() == gtk.RESPONSE_ACCEPT:
            filename = self.database.filename
            dstfile = dial.get_filename()
            if self.quit():
                shutil.copyfile(filename, dstfile)
                self.database.open_existing(dstfile)
                self.call_update_callback()
        dial.destroy()
                
                

    def import_from_old_database_activate(self, action):
        self.import_from_old_database()

    def import_from_old_database(self):
        if self.database.connection == None:
            return
        win = self.builder.get_object("main_window")
        ch = self.database.get_changes()
        if ch > 0:
            show_error(u'Перед импортом нужно завершить транзакцию выполните Rollback или Commit', win)
            return
        diag = gtk.FileChooserDialog(title = u'Открыть базу', parent = win, action = gtk.FILE_CHOOSER_ACTION_OPEN)
        diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
        fl = gtk.FileFilter()
        fl.add_mime_type('application/x-sqlite3')
        diag.set_filter(fl)
        if diag.run() == gtk.RESPONSE_ACCEPT:
            try:
                self.database.load_from_old_version(diag.get_filename())
            except Exception as e:
                show_and_print_error(e, win)
        diag.destroy()
        fl.destroy()

    def transaction_commit_activate(self, action):
        self.transaction_commit()

    def transaction_commit(self):
        if self.database.connection:
            self.database.commit()

    def transaction_rollback_activate(self, action):
        self.transaction_rollback()

    def transaction_rollback(self):
        if self.database.connection:
            self.database.rollback()
            self.call_update_callback()

    def close_activate(self, action):
        self.close()

    def close(self):
        if self.quit():
            self.set_main_title("Open Delas")
            self.call_update_callback()

    def open_database_activate(self, action):
        self.open_database()

    def open_database(self):
        if self.quit():
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
                    self.call_update_callback()
                except Exception as e:
                    show_error(e.__str__(), self.builder.get_object("main_window"))
                    print(traceback.format_exc())
            diag.destroy()
            fl.destroy()
        
    def set_main_title(self, title):
        self.builder.get_object("main_window").set_title(title)

    def quit(self):
        """returns True if you can quit"""
        try:
            self.database.close()
            self.global_data["current_account"] = None
        except Exception as e:
            show_error(e.__str__(), self.builder.get_object("main_window"))
            print(traceback.format_exc())
            return False
        return True

    def quit_activate(self, action):
        if self.quit():
            gtk.main_quit()

    def main_window_quit(self, window, evt):
        if self.quit():
            gtk.main_quit()
            return False
        return True
        
    def create_database_in_memory_activate(self, action):
        self.create_database_in_memory()

    def create_database_in_memory(self):
        if self.quit():
            self.database.create_new(":memory:")
            self.call_update_callback()
        
    def create_database_in_file(self):
        if self.quit():
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Новая база', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self.database.create_new(diag.get_filename())
                    self.call_update_callback()
                except Exception as e:
                    show_error(e.__str__(), self.builder.get_object("main_window"))
                    print(traceback.format_exc())
            diag.destroy()

    def create_database_activate(self, action):
        self.create_database_in_file()

    def update_widget(self):
        if self.database.connection:
            if self.database.filename == ":memory:":
                self.set_main_title(u'База данных в памяти')
            else:
                self.set_main_title(self.database.filename)
        else:
            self.set_main_title("Open Deals")
            
