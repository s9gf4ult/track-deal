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
        self.accounts_list = list_view_sort_control(self.builder.get_object("accounts_view"), [(u'Имя', gtk.CellRendererText()), (u'Начальный счет', gtk.CellRendererSpin()), (u'Текущий счет', gtk.CellRendererSpin())])
        self.account_list = list_view_sort_control(self.builder.get_object("account_view"), [(u'Свойство', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
        

    def update_widget(self):
        pass
    
    def add_account_activate(self, action):
        self.add_account()

    def delete_account_activate(self, action):
        pass

    def modify_account_activate(self, action):
        pass
    
