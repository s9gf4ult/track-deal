#!/bin/env python
# -*- coding: utf-8 -*-
import traceback
import gtk
from modifying_tab_control import modifying_tab_control

class main_window_controller(modifying_tab_control):
    def __init__(self, database, builder, update_callback):
        self.database = database
        self.builder = builder
        shorter(name, signal, *method):
            self.builder.get_object(name).connect(signal, *methid)

        shorter("quit", "activate", self.quit_activate)
        shorter("create_database", "activate", self.create_database_activate)
        shorter("open_database", "activate", self.open_database_activate)
        shorter("transaction_commit", "activate", self.transaction_commit_activate)
        shorter("transaction_rollback", "activate", self.transaction_rollback_activate)
        shorter("close_database", "activate", self.close_activate)
        shorter("create_database_in_memory", "activate", self.create_database_in_memory_activate)
        shorter("main_window", "delete-event", self.main_window_quit)


    def quit(self):
        """returns True if you can quit"""
        try:
            self.database.close()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())
            return False
        return True

    def quit_activate(self, action):
        if self.quit():
            gtk.main_quit()

    def main_window_quit(self, window, evt):
        if self.quit():
            return False
        return True
        
    def create_database_in_memory_activate(self, action):
        self.create_database_in_memory()

    def create_database_in_memory(self):
        if self.quit():
            self.database.create_new(":memory:")
            self.update_callback()
        
