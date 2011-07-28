#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sqlite3
from account_edit_control import account_edit_control
import gtk_view
from od_exceptions import *

class accounts_tab_controller(object):
    """
    \~russian
    \brief Контрол для вкладки со счетами
    """
    def __init__(self, parent):
        """
        \param parent instance of gtk_view
        """
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        def shorter(name, *method):
            self._parent.window.builder.get_object(name).connect("activate", *method)
        shorter("add_account", self.add_account_activate)
        shorter("delete_account", self.delete_account_activate)
        shorter("modify_account", self.modify_account_activate)
        shorter("set_current_account", self.set_current_account_activate)
        self.accounts_list = list_view_sort_control(self._parent.window.builder.get_object("accounts_view"), [(u'Имя', gtk.CellRendererText()), (u'Начальный счет', gtk.CellRendererSpin()), (u'Текущий счет', gtk.CellRendererSpin()), (u'Валюта', gtk.CellRendererText()), (u'Количество', gtk.CellRendererSpin(), int)])
        self.account_list = list_view_sort_control(self._parent.window.builder.get_object("account_view"), [(u'Свойство', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
        self._parent.window.builder.get_object("accounts_view").connect("row-activated", self.accounts_view_row_activated)

    def accounts_view_row_activated(self, tw, path, col):
        """
        \~russian
        \brief обработчик двойного нажатия на списке со счетами
        """
        self.set_current_account()
        self._parent.call_update_callback()

    def set_current_account_activate(self, action):
        self.set_current_account()
        self._parent.call_update_callback()

    def update(self):
        self.update_accounts_list()
        self.update_account_label()
        self.update_account_list()

    def update_account_label(self):
        if self._parent.connected():
            cac = self._parent.model.get_current_account()
            if cac != None:
                self._parent.window.builder.get_object("current_account_name_label").set_text(cac["name"])
            else:
                self._parent.window.builder.get_object("current_account_name_label").set_text("")
        else:
            self._parent.window.builder.get_object("current_account_name_label").set_text("")

    def update_account_list(self):
        """update list of properties and statistics of selected account
        \todo need implementation
        """
        pass

    def update_accounts_list(self):
        """update list of accounts"""
        if self._parent.connected():
            self.accounts_list.update_rows(map(lambda a: (a["name"], a["first_money"], a["current_money"], a["money_name"], a["deals"]), self._parent.model.list_view_accounts(["name"])))
        else:
            self.accounts_list.make_model()
            
    def add_account_activate(self, action):
        self.add_account()

    def add_account(self):
        """runs account adder dialog and adds account to the database"""
        if self._parent.connected():
            self._parent.account_edit.reset_widget()
            ret = self._parent.account_edit.run()
            if ret == gtk.RESPONSE_ACCEPT:
                try:
                    data = self._parent.account_edit.get_data()
                    self._parent.model.tacreate_account(data["name"], data["money_name"], data["money_count"], gethash(data, "comment"))
                except Exception as e:
                    show_and_print_error(e, self._parent.window.builder.get_object("main_window"))
            self._parent.call_update_callback()
                    

    def delete_account_activate(self, action):
        self.delete_account()

    def delete_account(self):
        """delete selected account"""
        if self._parent.connected():
            c = self._parent.window.builder.get_object("accounts_view")
            (mod, it) = c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                if self._parent.model.get_account(acname) != None:
                    if self._parent.model.assigned_account_deals(acname) > 0 or self._parent.model.assigned_account_positions(acname) > 0:
                        ret = query_yes_no("У счета есть сделки и/или позиции, удалить счет вместе с ними ?", self._parent.window.builder.get_object("main_window"))
                        if  ret <> gtk.RESPONSE_YES:
                            return
                    self._parent.model.taremove_account(acname)
                    self._parent.call_update_callback()
                

    def modify_account_activate(self, action):
        self.modify_account()

    def modify_account(self):
        """runs account dialog and modifies selected account"""
        if self._parent.connected():
            c = self._parent.window.builder.get_object("accounts_view")
            (mod, it) =  c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                acc = self._parent.model.get_account(acname)
                if acc != None:
                    self._parent.account_edit.reset_widget()
                    self._parent.account_edit.set_name(acc["name"])
                    self._parent.account_edit.set_comment(gethash(acc, "comments"))
                    self._parent.account_edit.set_currency(self._parent.model.get_money(acc["money_id"])["name"])
                    self._parent.account_edit.set_first_money(acc["money_count"])
                    ret = self._parent.account_edit.run()
                    if ret == gtk.RESPONSE_ACCEPT:
                        dd = self._parent.account_edit.get_data()
                        self._parent.model.tachange_account(acc["id"], dd["name"], dd["money_name"], dd["money_count"], dd["comment"])
                    self._parent.call_update_callback()

    def set_current_account(self):
        """
        \~russian
        \brief Устанавливает выделенный в списке счет текущим
        \note it does not call \ref gtk_view.call_update_callback to update view
        """
        if not self._parent.connected():
            return
        tw = self._parent.window.builder.get_object("accounts_view")
        (mod, it) = tw.get_selection().get_selected()
        if it != None:
            self._parent.model.taset_current_account(tw.get_model().get_value(it, 0))
