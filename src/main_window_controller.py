#!/bin/env python
# -*- coding: utf-8 -*-
import traceback
import shutil
import gtk
from modifying_tab_control import modifying_tab_control
from common_methods import *

class main_window_controller(object):
    """
    \~russian
    \brief Контрол для окна
    \par
    Нужен для обработки событий открытия закрытия базы, обновления заголовка окна/
    """
    def __init__(self, parent):
        """
        \~russian
        \param parent представление gtk_view
        """
        self._parent = parent
        self.builder = make_builder('glade/main_window.glade')
        def shorter(name, signal, *method):
            self.builder.get_object(name).connect(signal, *method)

        shorter("quit", "activate", self.quit_activate)
        shorter("create_database", "activate", self.create_database_activate)
        shorter("open_database", "activate", self.open_database_activate)
        shorter("close_database", "activate", self.close_activate)
        shorter("create_database_in_memory", "activate", self.create_database_in_memory_activate)
        shorter("main_window", "delete-event", self.main_window_quit)
        shorter("save_as", "activate", self.save_as_activate)
        shorter("add_papers", "activate", self.add_papers_activate)
        shorter('edit_points', 'activate', self.edit_points_activate)
        shorter('edit_currencies', 'activate', self.edit_currencies_activate)

    def edit_currencies_activate(self, action):
        """\brief edit currencies action handler
        \param action
        """
        if not self._parent.connected():
            return
        ret = self._parent.currency.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.model.recalculate_all_temporary()
            self._parent.call_update_callback()

    def edit_points_activate(self, action):
        """\brief 
        \param action
        """
        self._parent.points.run()


    def call_points(self, action):
        self.points.run()

    def save_as_activate(self, action):
        self.save_as()

    def save_as(self):
        if not self._parent.connected():
            return
        win = self.builder.get_object("main_window")
        # ch = self._parent.model.get_changes()
        # if ch > 0:
        #     show_error(u'Перед сохранением нужно завершить транзакцию выполните Rollback или Commit', win)
        #     return
        filename = self._parent.model._connection_string
        if filename == ":memory:":
            return
        dial = gtk.FileChooserDialog(title = u'Сохранить как', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE, buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        if dial.run() == gtk.RESPONSE_ACCEPT:
            dial.hide()
            dstfile = dial.get_filename()
            if self._parent.disconnect():
                try:
                    shutil.copyfile(filename, dstfile)
                    self._parent.model.open_existing(dstfile)
                    self.call_update_callback()
                except Exception as e:
                    show_and_print_error(e, win)
        dial.destroy()
                
                

    def import_from_old_database_activate(self, action):
        self.import_from_old_database()

    def import_from_old_database(self):
        if self._parent.model.connection == None:
            return
        win = self.builder.get_object("main_window")
        ch = self._parent.model.get_changes()
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
                self._parent.model.load_from_old_version(diag.get_filename())
            except Exception as e:
                show_and_print_error(e, win)
        diag.destroy()
        fl.destroy()

    def transaction_commit_activate(self, action):
        self.transaction_commit()

    def transaction_commit(self):
        if self._parent.model.connection:
            self._parent.model.commit()

    def transaction_rollback_activate(self, action):
        self.transaction_rollback()

    def transaction_rollback(self):
        if self._parent.connected():
            self._parent.model.rollback()
            self.call_update_callback()

    def close_activate(self, action):
        self.close()

    def close(self):
        if self._parent.disconnect():
            self._parent.call_update_callback()

    def open_database_activate(self, action):
        self.open_database()

    def open_database(self):
        if self._parent.disconnect():
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Открыть базу', parent = win, action = gtk.FILE_CHOOSER_ACTION_OPEN)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            fl = gtk.FileFilter()
            fl.add_mime_type('application/x-sqlite3')
            diag.set_filter(fl)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self._parent.open_existing_sqlite(diag.get_filename())
                except Exception as e:
                    show_error(e.__str__(), self.builder.get_object("main_window"))
                    print(traceback.format_exc())
            diag.destroy()
            fl.destroy()
            self._parent.call_update_callback()
        
    def set_main_title(self, title):
        self.builder.get_object("main_window").set_title(title)


    def quit_activate(self, action):
        if self._parent.disconnect():
            self._parent.quit()

    def main_window_quit(self, window, evt):
        if self._parent.disconnect():
            self._parent.quit()
            return False
        return True
        
    def create_database_in_memory_activate(self, action):
        self.create_database_in_memory()

    def create_database_in_memory(self):
        if self._parent.disconnect():
            self._parent.create_new_sqlite(":memory:")
            self._parent.call_update_callback()
        
    def create_database_in_file(self):
        if self._parent.disconnect():
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Новая база', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self._parent.create_new_sqlite(diag.get_filename())
                except Exception as e:
                    show_and_print_error(e, self.builder.get_object("main_window"))
            diag.destroy()
            self._parent.call_update_callback()


    def create_database_activate(self, action):
        self.create_database_in_file()

    def update(self):
        """update main window
        """
        if self._parent.connected():
            if self._parent.model._connection_string == ":memory:":
                self.set_main_title(u'База данных в памяти')
            else:
                self.set_main_title(self._parent.model._connection_string)
        else:
            self.set_main_title("Open Deals")
            
    def run(self, ):
        """show main window
        """
        win = self.builder.get_object("main_window")
        win.show_all()

    def add_papers_activate(self, action):
        """\brief add papers action activate handler
        \param action
        """

        self.call_paper_adder()

    def call_paper_adder(self, ):
        """\brief call paper_padder dialog
        """
        if not self._parent.connected():
            return
        self._parent.paper_adder.update_adder()
        ret = self._parent.paper_adder.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.model.recalculate_all_temporary()
            self._parent.call_update_callback()
        

