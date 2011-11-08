#!/bin/env python
# -*- coding: utf-8 -*-
## account_in_out_controller ##

from combo_select_control import combo_select_control
from common_methods import make_builder, format_number, show_and_print_error, \
    is_null_or_empty
from datetime_control import datetime_control
from list_view_sort_control import list_view_sort_control
from od_exceptions import od_exception_db_integrity_error
from sys import maxint
from time_control import time_control
import gtk


class account_in_out_controller(object):
    """\brief entry withdrawall from the account dialog controller
    """
    def __init__(self, parent):
        """\brief 
        \param parent
        """
        self._parent = parent
        self.builder = make_builder('glade/account_in_out.glade')
        def shobject(name):
            return self.builder.get_object(name)

        self.list = list_view_sort_control(shobject('in_out_list'), [['id', int], (u'Счет', gtk.CellRendererText()), (u'Дата', gtk.CellRendererText()), (u'Деньги', gtk.CellRendererText())])
        self.account = combo_select_control(shobject('account'))
        time = time_control(shobject('hour'), shobject('minute'), shobject('second'))
        self.datetime = datetime_control(shobject('calendar'), time, year = shobject('year'), month = shobject('month'), day = shobject('day'))
        self.amount = shobject('amount')
        self.amount.set_digits(2)
        self.amount.get_adjustment().configure(0, -maxint, maxint, 1, 100, 0)
        self.comment = shobject('comment').get_buffer()
        self.window = shobject('account_in_out')
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.window.set_transient_for(self._parent.window.builder.get_object('main_window'))
        shobject('add').connect('clicked', self.add_clicked)
        shobject('delete').connect('clicked', self.delete_clicked)
        shobject('modify').connect('clicked', self.modify_clicked)
        shobject('in_out_list').connect('cursor-changed', self.cursor_changed)

    def cursor_changed(self, treeview):
        """\brief entry withdrawall cursor changed handler 
        \param treeview
        """
        sel = self.list.get_selected_row()
        if sel != None:
            accio = self._parent.model.get_account_in_out(sel[0])
            self.account.set_value(accio['account_id'])
            self.datetime.set_datetime(accio['datetime'])
            self.amount.set_value(accio['money_count'])
            self.comment.set_text(accio['comment'])
            
    def add_clicked(self, button):
        """\brief 
        \param button
        """
        if self.check_entry_ready():
            try:
                aid = self._parent.model.create_account_in_out(self.account.get_value(),
                                                               self.datetime.get_datetime(),
                                                               self.amount.get_value(),
                                                               self.comment.get_text(self.comment.get_start_iter(), self.comment.get_end_iter()))
                acc = self._parent.model.get_account(self.account.get_value())
                self.list.add_row((aid, acc['name'], self.datetime.get_datetime().date().isoformat(), format_number(self.amount.get_value())))
            except od_exception_db_integrity_error:
                pass
        
    def delete_clicked(self, button):
        """\brief 
        \param button
        """
        sel = self.list.get_selected_row()
        if sel != None:
            try:
                self._parent.model.remove_account_in_out(sel[0])
                self.list.delete_selected()
            except od_exception_db_integrity_error:
                pass
        
    def modify_clicked(self, button):
        """\brief 
        \param button
        """
        if self.check_entry_ready():
            sel = self.list.get_selected_row()
            if sel != None:
                try:
                    self._parent.model.change_account_in_out(sel[0],
                                                             self.account.get_value(),
                                                             self.datetime.get_datetime(),
                                                             self.amount.get_value(),
                                                             self.comment.get_text(self.comment.get_start_iter(),
                                                                                   self.comment.get_end_iter()))
                    acc = self._parent.model.get_account(self.account.get_value())
                    self.list.save_value_in_selected(1, acc['name'])
                    self.list.save_value_in_selected(2, self.datetime.get_datetime().date().isoformat())
                    self.list.save_value_in_selected(3, self.amount.get_value())
                except od_exception_db_integrity_error:
                    pass

    def update(self, ):
        """\brief update posible account fields and list of withdrawalls
        """
        if self._parent.connected():
            accs = self._parent.model.list_accounts(['name'])
            self.account.update_answers(map(lambda a: (a['id'], a['name']), accs))
            cacc = self._parent.model.get_current_account()
            if cacc != None:
                self.account.set_value(cacc['id'])
            withdr = self._parent.model.list_view_account_in_out().fetchall()
            self.list.update_rows(map(lambda a: (a['id'], a['account_name'], a['datetime'].date().isoformat(), format_number(a['money_count'])) , withdr))
                
    def run(self, ):
        """\brief run dialog window
        """
        if self._parent.connected():
            self._parent.model.start_transacted_action('modify some account entry withdrawall money')
            ret = None
            try:
                ret = self.window.run()
                if ret == gtk.RESPONSE_ACCEPT:
                    self._parent.model.commit_transacted_action()
                else:
                    self._parent.model.rollback()
            except Exception as e:
                self._parent.model.rollback()
                show_and_print_error(e, self.window)
            self.window.hide()
            return ret

    def check_entry_ready(self, ):
        """\brief return true if all fields completely selected
        """
        if is_null_or_empty(self.account.get_value()):
            return False
        if is_null_or_empty(self.datetime.get_datetime()):
            return False
        if abs(self.amount.get_value()) < 0.001:
            return False
        return True
