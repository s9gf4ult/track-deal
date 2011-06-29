#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sqlite3
from account_edit_control import account_edit_control
import gtk_view

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
            self._parent.builder.get_object(name).connect("activate", *method)
        shorter("add_account", self.add_account_activate)
        shorter("delete_account", self.delete_account_activate)
        shorter("modify_account", self.modify_account_activate)
        shorter("set_current_account", self.set_current_account_activate)
        self.accounts_list = list_view_sort_control(self._parent.builder.get_object("accounts_view"), [(u'Имя', gtk.CellRendererText()), (u'Начальный счет', gtk.CellRendererSpin()), (u'Текущий счет', gtk.CellRendererSpin()), (u'Валюта', gtk.CellRendererText()), (u'Количество', gtk.CellRendererSpin(), int)])
        self.account_list = list_view_sort_control(self._parent.builder.get_object("account_view"), [(u'Свойство', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
        self._parent.builder.get_object("accounts_view").connect("row-activated", self.accounts_view_row_activated)

    def accounts_view_row_activated(self, tw, path, col):
        """
        \~russian
        \brief обработчик двойного нажатия на списке со счетами
        """
        self.set_current_account()
        self.call_update_callback()

    def set_current_account_activate(self, action):
        self.set_current_account()
        self.call_update_callback()

    def update(self):
        self.update_accounts_list()
        self.update_account_label()
        self.update_account_list()

    def update_account_label(self):
        if self._model.connection != None:
            (acname, ) = self._model.connection.execute("select name from accounts where id = ?", (gethash(self.global_data, "current_account"),)).fetchone() or (None, )
            self._parent.builder.get_object("current_account_name_label").set_text(acname != None and acname or "")
        else:
            self._parent.builder.get_object("current_account_name_label").set_text("")

    def update_account_list(self):
        """update list of properties and statistics of selected account"""
        pass

    def update_accounts_list(self):
        """update list of accounts"""
        if self._model.connection:
            self.accounts_list.update_rows(self._model.connection.execute("select name, first_money, last_money, currency, deals_count from accounts_view").fetchall())
        else:
            self.accounts_list.update_rows([])
            
    def add_account_activate(self, action):
        self.add_account()

    def add_account(self):
        """runs account adder dialog and adds account to the database"""
        if self._parent.connected():
            self._parent.account_edit.reset_widget()
            ret = self._parent.account_edit.run()
            if ret != None:
                try:
                    data = self._parent.acount_edit.get_data()
                    self._parent.model.tacreate_account(data["name"], data["money_name"], data["money_count"], gethash(data, "comment"))
                except Exception as e:
                    show_and_print_error(e, self._parent.builder.get_object("main_window"))
                    
                    

    def delete_account_activate(self, action):
        self.delete_account()

    def delete_account(self):
        """delete selected account"""
        if self._parent.connected():
            c = self._parent.builder.get_object("accounts_view")
            (mod, it) = c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                if self._parent.model.get_account(acname) != None:
                    dial = gtk.Dialog(title = u'Удалить счет', parent = self._parent.builder.get_object("main_window"), flags = gtk.DIALOG_MODAL, buttons = (gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
                    dial.get_content_area().pack_start(gtk.Label(u'Правда хотите удалить счет ?'))
                    dial.show_all()
                    ret = dial.run()
                    dial.destroy()
                    if ret != gtk.RESPONSE_NO and ret != gtk.RESPONSE_YES:
                        return
                    if  ret == gtk.RESPONSE_YES:
                        self._parent.model.taremove_account(acname)
                self.set_current_account()
                self._parent.call_update_callback()
                

    def modify_account_activate(self, action):
        self.modify_account()

    def modify_account(self):
        """runs account dialog and modifies selected account"""
        if self._model.connection:
            c = self._parent.builder.get_object("accounts_view")
            (mod, it) =  c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                (id, name, first_money, currency) = self._model.connection.execute("select id, name, first_money, currency from accounts where name = ?", (acname, )).fetchone() or (None, None, None, None)
                if name != None:
                    self.account_edit.update_widget(map(lambda a: a[0], self._model.connection.execute("select distinct currency from accounts order by currency")))
                    self.account_edit.load_to_widget({"name" : name,
                                                      "first_money" : first_money,
                                                      "currency" : currency})
                    ret = self.account_edit.run()
                    if ret != None:
                        self._model.connection.execute("update accounts set name = ?, first_money = ?, currency = ? where id = ?", (ret['name'], ret['first_money'], ret['currency'], id))
                        self.call_update_callback()

    def set_current_account(self):
        """
        \~russian
        \brief Устанавливает выделенный в списке счет текущим
        """
        if not self._parent.connected():
            return
        tw = self._parent.builder.get_object("accounts_view")
        (mod, it) = tw.get_selection().get_selected()
        if it != None:
            self._parent.model.taset_current_account(tw.get_model().get_value(it, 0))
