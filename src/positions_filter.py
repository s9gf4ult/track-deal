#!/bin/env python
# -*- coding:utf-8 -*-
from positions_filter_control import *
from common_methods import *

class positions_filter:
    plus = []
    def __init__(self, parent):
        self._parent = parent
        self.dialog = positions_filter_control(self._parent.builder)

    def update_filter(self, ):
        """\brief update fields of the filter
        """
        self.update_digits()
        self.update_instruments()
        self.update_accounts()


    def update_digits(self, ):
        """\brief update digit fields in the filter to correctly choose the proper range
        """
        if not self._parent.connected():
            return
        for (widget, limname) in [(self.dialog.count, "count"),
                                  (self.dialog.price, "price"),
                                  (self.dialog.volume, "volume"),
                                  (self.dialog.plnet_acc, "percent_range"),
                                  (self.dialog.plnet_volume, "percent_volume_range"),
                                  (self.dialog.comm_plgross, "percent_comm_plgross"),
                                  (self.dialog.price_range, "steps_range_abs"),
                                  (self.dialog.plgross, "pl_gross_abs"),
                                  (self.dialog.plnet, "pl_net_abs"),
                                  (self.dialog.comm, "commission")]:
            limits = self._parent.model.get_positions_view_limits(limname)
            widget.set_lower_limit(limits[0])
            widget.set_upper_limit(limits[1])
        
    def update_instruments(self, ):
        """\brief update instrument check_control 
        """
        papers = self._parent.model.list_papers(['name'])
        self.dialog.check_instruments.update_rows(map(lambda a: (a["id"], a["name"]), papers))

    def update_accounts(self, ):
        """\brief update account check_control
        """
        accs = self._parent.model.list_accounts(['name'])
        self.dialog.check_accounts.update_rows(map(lambda a: (a["id"], a["name"]), accs))

    def run(self):
        self.dialog.run()

    def get_data(self, ):
        """\brief get data from the filter
        """
        
        
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
