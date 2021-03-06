#!/bin/env python
# -*- coding: utf-8 -*-
from common_methods import format_number, gethash, show_and_print_error, \
    query_yes_no
from list_view_sort_control import list_view_sort_control
from od_exceptions import od_exception_config_key_error
import gtk
import gtk_view

statistics_names = ['deals_count',
                    'profit_positions_count',
                    'positions_count',
                    'loss_positions_count',
                    'profit_positions_profit',
                    'loss_positions_loss',
                    'commission',
                    'profit_average',
                    'loss_average',
                    'profit_max_position',
                    'loss_max_position',
                    'volume',
                    'profit_positions_volume',
                    'loss_positions_volume',
                    'profit_days_count',
                    'loss_days_count',
                    'days_count',
                    'inactive_days_count',
                    'profit_long_positions_count',
                    'profit_short_positions_count',
                    'loss_long_positions_count',
                    'loss_short_positions_count',
                    'long_positions_count',
                    'short_positions_count',
                    'long_max_profit',
                    'long_max_loss',
                    'long_volume',
                    'short_max_profit',
                    'short_max_loss',
                    'short_volume',
                    'long_profit_average',
                    'long_loss_average',
                    'short_profit_average',
                    'short_loss_average',
                    'long_plnet_average',
                    'short_plnet_average',
                    'profit_day_max_positions_count',
                    'profit_day_average_positions_count',
                    'loss_day_max_positions_count',
                    'loss_day_average_positions_count',
                    'profit_day_max_profit',
                    'profit_day_average',
                    'loss_day_max_loss',
                    'loss_day_average',
                    'day_average']
                

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
        self.accounts_list = list_view_sort_control(self._parent.window.builder.get_object("accounts_view"), [['id', int], (u'Имя', gtk.CellRendererText()), (u'Начальный счет', gtk.CellRendererText()), (u'Текущий счет', gtk.CellRendererText()), (u'Валюта', gtk.CellRendererText())])
#        self.account_list = list_view_sort_control(self._parent.window.builder.get_object("account_view"), [(u'Свойство', gtk.CellRendererText()), (u'Значение', gtk.CellRendererText())])
#        self._parent.window.builder.get_object("accounts_view").connect("row-activated", self.accounts_view_row_activated)

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


    def flush_statistics(self):
        for name in statistics_names:
            obj = self._parent.window.builder.get_object(name)
            obj.set_text('0')
    
    
    def update_statistics(self):
        if not self._parent.connected():
            return
        cac = self._parent.get_model().get_current_account()
        if cac == None:
            self.flush_statistics()
            return
        stats = self._parent.get_model().list_account_statistics(cac['id']).fetchall() 
        statsh = {}
        for val in stats:
            statsh[val['parameter_name']] = val['value']
        for name in statistics_names:
            if statsh.has_key(name):
                obj = self._parent.window.builder.get_object(name)
                obj.set_text(format_number(statsh[name]))
            else:
                self._parent.window.builder.get_object(name).set_text('None')
    
    
    def update(self):
        self.update_accounts_list()
        self.update_account_label()
        self.update_statistics()

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
        """
        if not self._parent.connected():
            return
        cacc = self._parent.model.get_current_account()
        if cacc == None:
            self.account_list.update_rows([])
            return
        stats = self._parent.model.list_account_statistics(cacc['id']).fetchall()
        self.account_list.update_rows(map(lambda a: (a['parameter_name'], (format_number(a['value']) if isinstance(a['value'], (int, float)) else a['value'])), stats))

    def update_accounts_list(self):
        """update list of accounts"""
        try:
            self.accounts_list.set_odd_color(self._parent.settings.get_key('interface.odd_color'))
            self.accounts_list.set_even_color(self._parent.settings.get_key('interface.even_color'))
        except od_exception_config_key_error:
            pass
        if self._parent.connected():
            self.accounts_list.update_rows(map(lambda a: (a['account_id'], a["name"], format_number(a["first_money"]), format_number(a["current_money"]), a["money_name"]), self._parent.model.list_view_accounts(["name"]).fetchall()))
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
            row = self.accounts_list.get_selected_row()
            if row != None:
                if self._parent.model.assigned_account_deals(row[0]) > 0 or self._parent.model.assigned_account_positions(row[0]) > 0:
                    ret = query_yes_no("У счета есть сделки и/или позиции, удалить счет вместе с ними ?", self._parent.window.builder.get_object("main_window"))
                    if  ret <> gtk.RESPONSE_YES:
                        return
                self._parent.model.taremove_account(row[0])
                self._parent.call_update_callback()
                

    def modify_account_activate(self, action):
        self.modify_account()

    def modify_account(self):
        """runs account dialog and modifies selected account"""
        if self._parent.connected():
            row = self.accounts_list.get_selected_row()
            if row != None:
                acc = self._parent.model.get_account(row[0])
                self._parent.account_edit.reset_widget()
                self._parent.account_edit.set_name(acc['name'])
                self._parent.account_edit.set_comment(gethash(acc, "comments"))
                self._parent.account_edit.set_currency(self._parent.model.get_money(acc["money_id"])["name"])
                self._parent.account_edit.set_first_money(acc["money_count"])
                ret = self._parent.account_edit.run()
                if ret == gtk.RESPONSE_ACCEPT:
                    dd = self._parent.account_edit.get_data()
                    self._parent.model.tachange_account(acc["id"],
                                                        dd["name"],
                                                        dd["money_name"],
                                                        dd["money_count"],
                                                        ('' if gethash(dd, 'comment') == None else dd['comment']))
                self._parent.call_update_callback()

    def set_current_account(self):
        """
        \~russian
        \brief Устанавливает выделенный в списке счет текущим
        \note it does not call \ref gtk_view.call_update_callback to update view
        """
        if not self._parent.connected():
            return
        row = self.accounts_list.get_selected_row()
        if row != None:
            self._parent.model.taset_current_account(row[0])
