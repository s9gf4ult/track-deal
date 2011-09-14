#!/bin/env python
# -*- coding: utf-8 -*-
## history_dialog_controller ##

from common_methods import make_builder,show_and_print_error
from list_view_sort_control import list_view_sort_control
import gtk

class history_dialog_controller(object):
    """\brief controller for the history dialog
    """
    def __init__(self, parent):
        """\brief constructor
        \param parent
        """
        self._parent = parent
        self.builder = make_builder('glade/history_dialog.glade')
        def shobject(name):
            return self.builder.get_object(name)

        self.window = shobject('history_dialog')
        if self._parent != None:
            self.window.set_transient_for(self._parent.window.builder.get_object('main_window'))
            self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            self.window.set_position(gtk.WIN_POS_CENTER)
            
        self.window.add_buttons(gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL)
        shobject('head').connect('activate', self.head_activate)
        shobject('continue').connect('activate', self.continue_activate)
        shobject('rollback').connect('activate', self.rollback_activate)
        self.history_tree = shobject('history_tree')
        self.history = list_view_sort_control(self.history_tree, [['id', int], ('Название', gtk.CellRendererText(), str), ('Дата', gtk.CellRendererText(), str)])
        self.history_tree.connect('row-activated', self.tree_row_activated) 

    def head_activate(self, action):
        """\brief make selected head activated
        \param action
        """
        self.head_selected()

    def continue_activate(self, action):
        """\brief continue from head activated
        \param action
        """
        self.continue_from_head()
        
    def rollback_activate(self, action):
        """\brief rollback to selected activated
        \param action
        """
        self.rollback_selected()

    def tree_row_activated(self, treeview, path, view_column):
        """\brief double click on tree view
        \param treeview
        \param path
        \param view_column
        """
        self.rollback_selected()

    def rollback_selected(self, ):
        """\brief rollback to selected action
        """
        sel = self.history.get_selected_row()
        if sel == None:
            return
        try:
            self._parent.model.go_to_action(sel[0])
        except Exception as e:
            show_and_print_error(e, self.window)

    def continue_from_head(self, ):
        """\brief set history back to finite state
        """
        pass
