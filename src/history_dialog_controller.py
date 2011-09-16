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
        self.history = list_view_sort_control(self.history_tree, [('Порядок', gtk.CellRendererText(), int), ('*', gtk.CellRendererText(), str), ('Название', gtk.CellRendererText(), str), ('Дата', gtk.CellRendererText(), str)])
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
            self._parent.model.tago_to_action(sel[0])
            self.update()
        except Exception as e:
            show_and_print_error(e, self.window)

    def continue_from_head(self, ):
        """\brief set history back to finite state
        """
        try:
            self._parent.model.tago_to_head()
            self.update()
        except Exception as e:
            show_and_print_error(e, self.window)

    def head_selected(self, ):
        """\brief remove selected action and all above it
        """
        sel = self.history.get_selected_row()
        if sel == None:
            return
        try:
            stat = self._parent.model.get_action_stats(sel[0])
            dialog = gtk.MessageDialog(parent = self.window, flags = gtk.DIALOG_MODAL, type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_YES_NO, message_format = u'Этим дейтвием вы безвозвратно удалите {0} действий в которых содержиться {1} запросов на изменение базы данных.\n Вы желаете продолжить ?'.format(stat['actions_above'], stat['queries_above']))
            if dialog.run() == gtk.RESPONSE_YES:
                self._parent.model.taremove_action(sel[0])
                self.update()
        except Exception as e:
            show_and_print_error(e, self.window)
        dialog.destroy()
        
    def run(self, ):
        """\brief run dialog
        """
        self.update()
        ret = self.window.run()
        self.window.hide()
        return ret

    def update(self, ):
        """\brief update the data in actions list
        """
        actions = []
        cac = self._parent.model.get_current_action()
        for acc in self._parent.model.list_actions().fetchall():
            actions.append((acc['id'], ('*' if cac != None and acc['id'] == cac['id'] else ''), acc['autoname'], acc['datetime'].isoformat()))
            
        self.history.update_rows(actions)
            
