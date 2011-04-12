#!/bin/env python
# -*- coding: utf-8 -*-
from modifying_tab_control import modifying_tab_control
from list_view_sort_control import list_view_sort_control
import gtk
from common_methods import *
import sqlite3

class accounts_tab_controller(modifying_tab_control):
    def __init__(self, global_data, database, builder, update_callback, account_edit):
        self.builder = builder
        self.database = database
        self.account_edit = account_edit
        self.global_data = global_data
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
        if self.database.connection:
            self.account_edit.update_widget(map(lambda a: a[0], self.database.connection.execute("select distinct currency from accounts order by currency")))
            ret = self.account_edit.run()
            if ret != None:
                try:
                    self.database.make_account(ret['name'], ret['first_money'], ret['currency'])
                    self.update_accounts_list()
                except sqlite3.IntegrityError:
                    show_error(u'Счет с таким именем уже существует', self.builder.get_object("main_window"))
                except Exception as e:
                    show_error(e.__str__(), self.builder.get_object("main_window"))
                    print(traceback.format_exc())
                    
                    

    def delete_account_activate(self, action):
        self.delete_account()

    def delete_account(self):
        """delete selected account"""
        if self.database.connection:
            c = self.builder.get_object("accounts_view")
            (mod, it) = c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                if self.database.connection.execute("select count(d.id) from deals d inner join accounts a on d.account_id = a.id where a.name = ?", (acname, )).fetchone()[0] > 0:
                    dial = gtk.Dialog(title = u'Удалить счет', parent = self.builder.get_object("main_window"), flags = gtk.DIALOG_MODAL, buttons = (gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
                    dial.get_content_area().pack_start(gtk.Label(u'Удалить сделки привязанные к данному счету ?'))
                    dial.show_all()
                    ret = dial.run()
                    dial.destroy()
                    if ret != gtk.RESPONSE_NO and ret != gtk.RESPONSE_YES:
                        return
                    if  ret == gtk.RESPONSE_YES:
                        self.database.connection.execute("delete from deals where account_id in (select id from accounts where name = ?)", (acname, ))
                self.database.connection.execute("delete from accounts where name = ?", (acname, ))
                self.call_update_callback()
                

    def modify_account_activate(self, action):
        self.modify_account()

    def modify_account(self):
        """runs account dialog and modifies selected account"""
        if self.database.connection:
            c = self.builder.get_object("accounts_view")
            (mod, it) =  c.get_selection().get_selected()
            if it != None:
                acname = mod.get_value(it, 0)
                (id, name, first_money, currency) = self.database.connection.execute("select id, name, first_money, currency from accounts where name = ?", (acname, )).fetchone() or (None, None, None, None)
                if name != None:
                    self.account_edit.update_widget(map(lambda a: a[0], self.database.connection.execute("select distinct currency from accounts order by currency")))
                    self.account_edit.load_to_widget({"name" : name,
                                                      "first_money" : first_money,
                                                      "currency" : currency})
                    ret = self.account_edit.run()
                    if ret != None:
                        self.database.connection.execute("update accounts set name = ?, first_money = ?, currency = ? where id = ?", (ret['name'], ret['first_money'], ret['currency'], id))
                        self.call_update_callback()

    def account_cursor_changed(self, tw):
        self.update_account_list()
        (mod, it) = tw.get_selection().get_selected()
        if it != None and self.database.connection != None:
            (self.global_data["current_account"], ) = self.database.connection.execute("select id from accounts where name = ?", (tw.get_model.get_value(it, 0), )).fetchone() or (None)
            
