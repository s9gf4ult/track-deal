#!/bin/env python
# -*- coding: utf-8 -*-
## currency_edit_control ##

from list_view_sort_control import list_view_sort_control

class currency_edit_control(object):
    """\~russian
    \brief Контрол для редактирования списка известных валют
    """
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
        shobject("currency_edit_name").connect("focus-out-event", self.name_focus_leave)
        shobject("currency_edit_full_name").connect("focus-out-event", self.full_name_focus_leave)
        shobject("currency_edit_list").connect("cursor-changed", self.list_cursor_changed)
        shobject("currency_edit_add").connect("clicked", self.add_clicked)
        shobject("currency_edit_delete").connect("clicked", self.delete_clicked)
        self.currency_list = list_view_sort_control(shobject("currency_edit_list"), [("id", gtk.CellRendererText()),
                                                                                     ("Имя", gtk.CellRendererText())])
        
    def name_focus_leave(self, widget, event):
        """\brief name field focus leav handler
        \param widget
        \param event
        """
        pass

    def full_name_focus_leave(self, widget, event):
        """\brief full name focus leave handler
        \param widget
        \param event
        """
        pass

    def add_clicked(self, button):
        """\brief add button clicked handler
        \param button
        """
        pass

    def delete_clicked(self, button):
        """\brief delete button clicked handler
        \param button
        """
        pass

    def list_cursor_changed(self, treeview):
        """\brief cursor changed handler
        \param treeview
        """
        pass




