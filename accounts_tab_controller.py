#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import list_view_sort_control
import gtk

class accounts_tab_controller(modifying_tab_control):
    def __init__(self, database, builder, update_callback):
        self.builder = builder
        self.database = database
        self.update_callback = update_callback
        def shorter(name, *method):
            self.builder.get_object(name).connect("activate", *method)
        shorter("add_account", self.add_account_activate)
        shorter("delete_account", self.delete_account_activate)
        shorter("modify_account", self.modify_account_activate)
        self.accounts_list = list_view_sort_control(self.builder.get_object("accounts_view"), [(u'Имя', gtk.CellRendererText()), (u'Начальный счет', gtk.CellRendererSpin()), (u'Текущий счет', gtk.CellRendererSpin()), (u'Валюта', gtk.CellRendererText())])
        self.account_list = list_view_sort_control(self.builder.get_object("account_view"), [(u'Свойство', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
        self.builder.get_object("accounts_view").connect("cursor-changed", self.account_cursor_changed)
        

    def update_widget(self):
        self.update_accounts_list()
        self.update_account_list()

    def update_account_list(self):
        """update list of properties and statistics of selected account"""
        pass

    def update_accounts_list(self):
        """update list of accounts"""
        if self.database.connection:
            u = self.database.connection.execute("select a.name, a.first_money, (a.first_money + sum(d.deal_sign * d.volume)), a.currency from accounts a inner join deals d on d.account_id = a.id where d.not_actual is null group by a.name").fetchall()
            u += self.database.connection.execute("select a.name, a.first_money, a.first_money, a.currency from accounts a where not exists(select * from deals where account_id = a.id and not_actual is null)").fetchall()
            self.accounts_list.update_rows(u)
            
    def add_account_activate(self, action):
        self.add_account()

    def add_account(self):
        """runs account adder dialog and adds account to the database"""
        pass

    def delete_account_activate(self, action):
        self.delete_account()

    def delete_account(self):
        """delete selected account"""
        pass

    def modify_account_activate(self, action):
        self.modify_account()

    def modify_account(self):
        """runs account dialog and modifies selected account"""
        pass

    def account_cursor_changed(self, tw):
        self.update_account_list()
            
