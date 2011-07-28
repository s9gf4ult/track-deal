#!/bin/env python
# -*- coding: utf-8 -*-
## currency_edit_control ##

from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sqlite3

class currency_edit_control(object):
    """\~russian
    \brief Контрол для редактирования списка известных валют
    """

    ## gtk.TextBuffer instance with full name
    full_name = None

    ## gtk.Entry instance with name
    name = None

    ## gtk.Dialog instance
    window = None
    
    def __init__(self, parent):
        """
        \param parent instance of \ref gtk_view.gtk_view
        """
        self._parent = parent
        self.builder = make_builder('glade/currency_edit.glade')
        def shobject(name):
            return self.builder.get_object(name)
        self.window = shobject("currency_edit")
        self.window.set_transient_for(self._parent.window.builder.get_object('main_window'))
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.name = shobject("currency_edit_name")
        fn = shobject("currency_edit_full_name")
        self.full_name = fn.get_buffer()
        shobject("currency_edit_list").connect("cursor-changed", self.list_cursor_changed)
        shobject("currency_edit_add").connect("clicked", self.add_clicked)
        shobject("currency_edit_delete").connect("clicked", self.delete_clicked)
        shobject("currency_edit_save").connect("clicked", self.save_clicked)
        self.currency_list = list_view_sort_control(shobject("currency_edit_list"), [["id", int],
                                                                                     ("Имя", gtk.CellRendererText()),
                                                                                     ["full_name", str]])
        

    def add_clicked(self, button):
        """\brief add button clicked handler
        \param button
        """
        self.new_currency()

    def delete_clicked(self, button):
        """\brief delete button clicked handler
        \param button
        """
        self.delete_row()

    def list_cursor_changed(self, treeview):
        """\brief cursor changed handler
        \param treeview
        """
        self.update_fields()

    def save_clicked(self, button):
        """\brief save button handler
        \param button
        """
        self.save_current()


    def new_currency(self, ):
        """\brief create new currency
        """
        if is_blank(self.name.get_text()):
            return
        mid = None
        name = self.name.get_text()
        full_name = self.full_name.get_text(self.full_name.get_start_iter(), self.full_name.get_end_iter())
        try:
            mid = self._parent.model.create_money(name, full_name)
        except sqlite3.IntegrityError:
            pass
        else:
            self.currency_list.add_row((mid, name, full_name))
            self.name.set_text("")
            self.full_name.set_text("")
            
    def delete_row(self, ):
        """\brief delete selected row from currency list
        """
        row = self.currency_list.get_selected_row()
        if row == None:
            return 
        try:
            if self._parent.model.assigned_to_money_accounts(row[0]) > 0:
                if query_yes_no("Есть привязанные к валюте счета. Удалить вместе со счетами ?", self.window) <> gtk.RESPONSE_YES:
                    return
            self._parent.model.remove_money(row[0])
        except sqlite3.IntegrityError:
            pass
        else:
            self.currency_list.delete_selected()
        
        
    def update_fields(self, ):
        """\brief update fields according to selected row
        """
        r = self.currency_list.get_selected_row()
        self.name.set_text(r[1])
        self.full_name.set_text(r[2])
        
    def run(self, ):
        """\brief run the dialog
        \retval gtk.RESPONSE_ACCEPT - data has been saved
        \retval gtk.RESPONSE_CANCEL - cancel button was clicked
        """
        self.reset_fields()
        self.load_currency()
        self._parent.model.start_transacted_action("edit some money objects")
        ret =  self.window.run()
        self.window.hide()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.model.commit_transacted_action()
        else:
            self._parent.model.rollback()
        return ret


    def reset_fields(self, ):
        """\brief reset all fields and currency list
        """
        self.name.set_text("")
        self.full_name.set_text("")
        self.currency_list.make_model()

    def load_currency(self, ):
        """\brief load currency list from the database
        """
        if self._parent.connected():
            mns = self._parent.model.list_moneys(["name"])
            self.currency_list.update_rows(map(lambda a: (a["id"], a["name"], a["full_name"]), mns))

    def save_current(self, ):
        """\brief save data into current row
        """
        row = self.currency_list.get_selected_row()
        if row == None:
            return

        name = self.name.get_text()
        full_name = self.full_name.get_text(self.full_name.get_start_iter(), self.full_name.get_end_iter())
        try:
            self._parent.model.change_money(row[0], name = name, full_name = full_name)
        except sqlite3.IntegrityError:
            pass
        else:
            self.currency_list.save_value_in_selected(1, name)
            self.currency_list.save_value_in_selected(2, full_name)
