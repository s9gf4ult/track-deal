#/bin/env python
# -*- coding: utf-8 -*-
from deals_filter_control import deals_filter_control
import time
from common_methods import *


class deals_filter():

    def run(self):
        ret = self.dialog.run()
        return ret
    
        
    def prepare_filter(self, ):
        """\brief prepare filter values getting if need from the database
        """
        if not self._parent.connected():
            return
        papers = self._parent.model.list_papers(["name"])
        upps = map(lambda a: (a["id"], a["name"]), papers)
        accounts = self._parent.model.list_accounts(["name"])
        uaccs = map(lambda a: (a["id"], a["name"]), accounts)
        self.dialog.update_widget(count_range = self._parent.model.get_deals_count_range(),
                                  price_range = self._parent.model.get_deals_price_range(),
                                  comm_range = self._parent.model.get_deals_commission_range(),
                                  volume_range = self._parent.model.get_deals_volume_range(),
                                  stock_list = upps,
                                  accounts_list = uaccs)
        
        
    def __init__(self, parent):
        self._parent = parent
        self.dialog = deals_filter_control(self._parent.builder)
        

    def get_conditions(self, ):
        """\brief return string with where part
        \retval None if no one row must be displayed
        \retval ("", []) tuple if no conditions
        \retval (string with condition, list with arguments) if there is conditions for query
        """
        args = []
        conds = []
        # datetime conditions
        solve_lower_upper(args, conds, "datetime",
                          self.dialog.datetime_range.get_lower_datetime(),
                          self.dialog.datetime_range.get_upper_datetime())

        # instruments selected
        solve_field_in(args, conds, "paper_id",
                       map(lambda a: a[0], self.dialog.instruments.get_checked_rows()))
        
        # numerical fields
        for (field_name, control) in [("count", self.dialog.count),
                                      ("points", self.dialog.price),
                                      ("commission", self.dialog.comm),
                                      ("volume", self.dialog.volume)]:
            solve_lower_upper(args, conds, field_name,
                              control.get_lower_value(),
                              control.get_upper_value())

        # position
        inpos = self.dialog.position.get_value()
        if inpos <> None:
            if inpos:
                conds.append("position_id is not null")
            else:
                conds.append("position_id is null")

        # direction
        direct = self.dialog.direction.get_value()
        if direct <> None:
            conds.append("direction = ?")
            args.append(direct)

        # accounts
        cac = self._parent.model.get_current_account()
        ss = self.dialog.account_current.get_value()
        if ss == "current":
            if cac == None:
                return None             # we want to show deals from current account but current account is None
            conds.append("account_id = ?")
            args.append(cac["id"])
        elif ss == "all":
            pass
        elif ss == "select":
            selected = self.dialog.accounts.get_checked_rows()
            solve_field_in(args, conds, 'account_id',
                           map(lambda a: a[1], selected))
        return (reduce_by_string(" and ", conds), args)
        

    def get_rows(self, order_by):
        """\brief get filtred rows
        \param order_by - list of fields to order by
        \retval None if not connected
        \retval list of hash tables with keys like names in deals_view table of databse
        """
        if not self._parent.connected():
            return None
        cnds = self.get_conditions()
        if cnds == None:
            return []
        else:
            return self._parent.model.list_deals_view_with_condition(cnds[0], cnds[1], order_by).fetchall()

