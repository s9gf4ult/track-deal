#!/bin/env python
# -*- coding: utf-8 -*-
## currency_edit_control ##

from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *

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
        def shobject(name):
            return self._parent.builder.get_object(name)
        self.window = shobject("currency_edit")
        self.window.set_transient_for(shobject("main_window"))
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.name = shobject("currency_edit_name")
        self.name.connect("focus-out-event", self.name_focus_leave)
        fn = shobject("currency_edit_full_name")
        fn.connect("focus-out-event", self.full_name_focus_leave)
        self.full_name = fn.get_buffer()
        shobject("currency_edit_list").connect("cursor-changed", self.list_cursor_changed)
        shobject("currency_edit_add").connect("clicked", self.add_clicked)
        shobject("currency_edit_delete").connect("clicked", self.delete_clicked)
        self.currency_list = list_view_sort_control(shobject("currency_edit_list"), [["id", str],
                                                                                     ("Имя", gtk.CellRendererText()),
                                                                                     ["full_name", str]])
        
    def name_focus_leave(self, widget, event):
        """\brief name field focus leav handler
        \param widget
        \param event
        """
        return self.save_name()

    def full_name_focus_leave(self, widget, event):
        """\brief full name focus leave handler
        \param widget
        \param event
        """
        self.currency_list.save_value_in_selected(2, self.full_name.get_text(self.full_name.get_start_iter(), self.full_name.get_end_iter()))
        return False

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

    def new_currency(self, ):
        """\brief create new currency and focus curson on it
        """
        mid = None
        try:
            mid = self._parent.model.create_money("dummy")
        except:
            pass
        else:
            it = self.currency_list.add_row((mid, "dummy", ""))
            self.currency_list.select_by_iter(it)
        
    def delete_row(self, ):
        """\brief delete selected row from currency list
        """
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
        self._parent.model.commit_transacted_action()
        return ret

    # def check_data(self, ):
    #     """\brief check if data can be saved in the database
    #     \retval True - data can be saved
    #     \retval False
    #     """
    #     rows = map(lambda a: a[1], self.currency_list.get_rows())
    #     srows = set(rows)
    #     if len(srows) <> len(rows):
    #         show_error("Существуют не уникальные имена", self.window)
    #         return False
    #     for nn in rows:
    #         if is_blank(nn):
    #             show_error("Имя \"{0}\" состоит из пустых символов".format(nn), self.window)
    #             return False
    #     return True

    # def save_data(self, ):
    #     """\brief save dialog data into the database
    #     """
    #     if self._parent.connected():
    #         rows = self.currency_list.get_rows()
    #         rwids = set(filter(lambda x: isinstance(x, (int, long)), map(lambda a: a[0], rows)))
    #         self._parent.model.tashrink_money_by_id(rwids)
    #         new = map(lambda x: {"name" : x[1], "full_name" : x[2]}, filter(lambda a: is_null_or_empty(a[0]), rows))
    #         self._parent.model.tacreate_money_list(new)
        


    def save_name(self, ):
        """\brief try save name from field to selected row
        \retval False return always
        """
        row = self.currency_list.get_selected_row()
        if row <> None:
            if is_blank(row[1]):
                show_error("Имя пустое. Так незя", self.window)
                return False
            try:
                self._parent.model.change_money(row[0], name = self.name.get_text())
            except sqlite3.IntegrityError:
                pass
            except Exception as e:
                show_and_print_error(e)
            else:
                self.currency_list.save_value_in_selected(1, self.name.get_text())

                
        # names = map(lambda a: a[1], self.currency_list.get_rows())
        # txt = self.name.get_text()
        # if is_blank(txt) and row <> None and row[1] <> txt:
        #     show_error("Имя пустое", self.window)
        #     return False
        # elif txt in names and row <> None and row[1] <> txt:
        #     show_error("Имя уже существует", self.window)
        #     return False
        # else:
        #     self.currency_list.save_value_in_selected(1, self.name.get_text())
        #     return False

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
