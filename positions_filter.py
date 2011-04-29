#!/bin/env python
# -*- coding:utf-8 -*-
from positions_filter_control import *
from common_methods import *

class positions_filter:
    plus = []
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
            for (wid, field) in [(self.dialog.count, "count"),
                                 (self.dialog.price, "coast"),
                                 (self.dialog.volume, "volume"),
                                 (self.dialog.plnet_acc, "plnet_acc"),
                                 (self.dialog.plnet_volume, "plnet_volume"),
                                 (self.dialog.comm_plgross, "comm_pl_gross"),
                                 (self.dialog.price_range, "coast_range"),
                                 (self.dialog.plgross, "pl_gross_range"),
                                 (self.dialog.plnet, "pl_net_range"),
                                 (self.dialog.comm, "comm")]:
                (mmin, mmax) = self.database.connection.execute("select min({0}), max({0}) from positions_view".format(field)).fetchone()
                wid.set_lower_limit(mmin)
                wid.set_upper_limit(mmax)

    def _regen_selected(self):
        if self.database.connection != None:
            self.database.pset_selected_stocks(map(lambda a: a[0], self.dialog.check_instruments.get_checked_rows()))
            if self.dialog.account_current.get_value() == "current" and gethash(self.global_data, "current_account") != None:
                self.database.pset_selected_accounts([self.database.connection.execute("select name from accounts where id = ? limit 1", (self.global_data["current_account"],)).fetchone()[0]])
            elif self.dialog.account_current.get_value() == "select":
                self.database.pset_selected_accounts(map(lambda a: a[0], self.dialog.check_accounts.get_checked_rows()))
            

    def run(self):
        self._prepare_filter()
        self.dialog.run()
        
    def get_ids(self, fields, order_by):
        if self.database.connection == None or (gethash(self.global_data, "current_account") == None and self.dialog.account_current.get_value() == "current"):
            return []
        self.plus = []
        self._prepare_filter()
        self._regen_selected()
        gets = reduce_by_string(", ", map(lambda a: u'p.{0}'.format(a), fields))
        froms = self._get_from()
        wheres = self._get_where()
        orders = self._get_order_by(order_by)
        query = u'select {0} from {1}'.format(gets, froms)
        if not is_null_or_empty(wheres):
            query += u' where {0}'.format(wheres)
        if not is_null_or_empty(orders):
            query += u' order by {0}'.format(orders)
        print(query)
        if is_null_or_empty(self.plus):
            return self.database.connection.execute(query)
        else:
            return self.database.connection.execute(query, self.plus)

    def _get_from(self):
        ret = u'pselected_stocks ss inner join positions_view p on ss.stock = p.ticket'
        if self.dialog.account_current.get_value() == "select" or (self.dialog.account_current.get_value() == "current" and gethash(self.global_data, "current_account") != None):
            ret += u' inner join pselected_accounts sa on sa.account_id = p.account_id'
        return ret
            

    def _get_where(self):
        conds = []
        def lower_upper(value, low, high):
            solve_lower_upper(self.plus, conds, value, low, high)
        for (value, lower, upper) in [(u'p.open_datetime', self.dialog.open_datetime.get_lower_datetime(), self.dialog.open_datetime.get_upper_datetime()),
                                      (u'p.close_datetime', self.dialog.close_datetime.get_lower_datetime(), self.dialog.close_datetime.get_upper_datetime()),
                                      (u'p.count', self.dialog.count.get_lower_value(), self.dialog.count.get_upper_value()),
                                      (u'p.coast', self.dialog.price.get_lower_value(), self.dialog.price.get_upper_value()),
                                      (u'p.volume', self.dialog.volume.get_lower_value(), self.dialog.volume.get_upper_value()),
                                      (u'p.plnet_acc', self.dialog.plnet_acc.get_lower_value(), self.dialog.plnet_acc.get_upper_value()),
                                      (u'p.plnet_volume', self.dialog.plnet_volume.get_lower_value(), self.dialog.plnet_volume.get_upper_value()),
                                      (u'p.comm_pl_gross', self.dialog.comm_plgross.get_lower_value(), self.dialog.comm_plgross.get_upper_value()),
                                      (u'p.coast_range', self.dialog.price.get_lower_value(), self.dialog.price.get_upper_value()),
                                      (u'p.comm', self.dialog.comm.get_lower_value(), self.dialog.comm.get_upper_value()),
                                      (u'p.duration', self.dialog.time_distance.get_lower_seconds(), self.dialog.time_distance.get_upper_seconds())]:
            lower_upper(value, lower, upper)
        ls = self.dialog.direction.get_value()
        if ls != None:
            lower_upper(u'p.direction', ls, ls)
        lp = self.dialog.loss_profit.get_value()
        if lp != None:
            lower_upper(u'p.profit', lp, lp)
        

        if len(conds) > 0:
            return reduce_by_string(" and ", conds)
        else:
            return None
        
        

    def _get_order_by(self, order_by):
        if is_null_or_empty(order_by):
            return None
        else:
            return u'p.{0}'.format(order_by)
