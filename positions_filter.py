#!/bin/env python
# -*- coding:utf-8 -*-
from common_methods import *
from positions_filter_control import *

class positions_filter:
    def __init__(self, global_data, builder, database):
        self.global_data = global_data
        self.builder = builder
        self.database = database
        self.dialog = positions_filter_control(self.builder)

    def _prepare_filter(self):
        if self.database.connection != None:
            for (wid, query) in [(self.dialog.check_accounts, "select distinct name from accounts"),
                                 (self.dialog.check_instruments, "select distinct security_name from deals")]:
                wid.update_rows(self.database.connection.execute(query))

    def _regen_selected(self):
        if self.database.connection != None:
            self.database.pset_selected_stocks(map(lambda a: a[0], self.dialog.check_instruments.get_selected_rows()))
            
            

    def run(self):
        self._prepare_filter()
        self.dialog.run()
        
    def get_ids(self, fields, order_by):
        gets = reduce_by_string(", ", map(lambda a: u'p.{0}'.format(a), fields))
        froms = self._get_from()
        wheres = self._get_where()
        orders = self._get_order_by(order_by)
        query = u'select {0} from {1}'.format(gets, froms)
        if not is_null_or_empty(wheres):
            query += u' where {0}'.format(wheres)
        if not is_null_or_empty(orders):
            query += u' order by {0}'.format(orders)
        return self.database.connection.execute(query)

    def _get_from(self):
        ret = u'pselected_stocks ss inner join positions_view p on ss.ticket = p.ticket'
        if self.dialog.account_current.get_value() == "select" or (self.dialog.account_current.get_value() == "current" and gethash(self.global_data, "current_account") != None):
            ret += u' inner join pselected_accounts sa on sa.account_id = p.account_id'
            

    def _get_where(self):
        return None

    def _get_order_by(self, order_by):
        return None
