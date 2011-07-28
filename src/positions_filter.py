#!/bin/env python
# -*- coding:utf-8 -*-
from positions_filter_control import *
from common_methods import *

class positions_filter:
    plus = []
    def __init__(self, parent):
        self._parent = parent
        self.dialog = positions_filter_control(self._parent)

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
                                  (self.dialog.price, "price_avg"),
                                  (self.dialog.volume, "volume_avg"),
                                  (self.dialog.plnet_acc, "percent_range"),
                                  (self.dialog.plnet_volume, "percent_volume_range_abs"),
                                  (self.dialog.comm_plgross, "percent_comm_plgross_abs"),
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

    def get_data(self, order_by = []):
        """\brief get data from the filter
        \return list of hashes, each hash table has keys like in the table 'positions_view'
        """
        if not self._parent.connected():
            return
        conds = self.get_conditions()
        if conds == None:
            return []
        else:
            return self._parent.model.list_positions_view_with_condition(conds[0], conds[1], order_by).fetchall()

    def get_conditions(self, ):
        """\brief return conditions created from filter dialog data
        \retval (str, list) where str is the "where" query part and list is a list of arguments for condition
        \retval ("", []) if no conditions
        \retval None if no one position must be returned
        """
        conds = []
        args = []
        for (field_name, lower, upper) in [("open_datetime", self.dialog.open_datetime.get_lower_datetime(), self.dialog.open_datetime.get_upper_datetime()),
                                           ("close_datetime", self.dialog.close_datetime.get_lower_datetime(), self.dialog.close_datetime.get_upper_datetime()),
                                           ("count", self.dialog.count.get_lower_value(), self.dialog.count.get_upper_value()),
                                           ("price_avg", self.dialog.price.get_lower_value(), self.dialog.price.get_upper_value()),
                                           ("volume_avg", self.dialog.volume.get_lower_value(), self.dialog.volume.get_upper_value()),
                                           ("percent_range_abs", self.dialog.plnet_acc.get_lower_value(), self.dialog.plnet_acc.get_upper_value()),
                                           ("percent_volume_range_abs", self.dialog.plnet_volume.get_lower_value(), self.dialog.plnet_volume.get_upper_value()),
                                           ("percent_comm_plgross_abs", self.dialog.comm_plgross.get_lower_value(), self.dialog.comm_plgross.get_upper_value()),
                                           ("steps_range_abs", self.dialog.price_range.get_lower_value(), self.dialog.price_range.get_upper_value()),
                                           ("pl_gross_abs", self.dialog.plgross.get_lower_value(), self.dialog.plgross.get_upper_value()),
                                           ("pl_net_abs", self.dialog.plnet.get_lower_value(), self.dialog.plnet.get_upper_value()),
                                           ("commission", self.dialog.comm.get_lower_value(), self.dialog.comm.get_upper_value()),
                                           ("duration", self.dialog.time_distance.get_lower_seconds(), self.dialog.time_distance.get_upper_seconds())]:
            solve_lower_upper(args, conds, field_name,  lower, upper)
            
        direct = self.dialog.direction.get_value()
        if direct<>None:
            conds.append('direction = ?')
            args.append(direct)

        loss_prof = self.dialog.loss_profit.get_value()
        if loss_prof <> None:
            if loss_prof > 0:
                conds.append('pl_net > 0')
            elif loss_prof < 0:
                conds.append('pl_net < 0')

        acc = self.dialog.account_current.get_value()
        if acc == 'current':
            cacc = self._parent.model.get_current_account()
            if cacc <> None:
                conds.append('account_id = ?')
                args.append(cacc['id'])
            else:
                return None
        elif acc == 'all':
            pass
        elif acc == 'select':
            chaccs = self.dialog.check_accounts.get_checked_rows()
            if is_null_or_empty(chaccs):
                return None
            else:
                solve_field_in(args, conds, 'account_id', map(lambda a: a[0], chaccs))

        instrs = self.dialog.check_instruments.get_checked_rows()
        if not is_null_or_empty(instrs):
            solve_field_in(args, conds, 'paper_id', map(lambda a: a[0], instrs))
        else:
            return None
        
        return (reduce_by_string(' and ', conds), args)
