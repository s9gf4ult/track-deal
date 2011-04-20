#/bin/env python
# -*- coding: utf-8 -*-
from deals_filter_control import deals_filter_control
import time
from common_methods import *


class iter_filter():
    def __init__(self, cursor):
        self.cursor = cursor

    def next(self):
        return self.cursor.next()[0]

class cursor_filter():
    def __init__(self, query, connection):
        # print(query)
        self.query = query
        self.connection = connection

    def __iter__(self):
        return iter_filter(self.connection.execute(self.query))

class cursor_empty():
    def __iter__(self):
        return empty_iter()

class empry_iter():
    def next(self):
        raise StopIteration()

class deals_filter():

    def run(self):
        self._prepare_filter()
        ret = self.dialog.run()
        self._regen_selected()
        return ret
    

    def get_ids(self, order_by, parent = False, fields = ["id"]):
        if not self.database.connection:
            return cursor_empty()
        self.plus = []
        fields = reduce_by_string(u', ', map(lambda a: u'd.{0}'.format(a), fields))
        fromf = self.get_from_part()
        ret = u'select {0} from {1}'.format(fields, fromf)
        wheref = self.get_where_part(parent)
        if not is_null_or_empty(wheref):
            ret += ' where {0}'.format(wheref)
        orderf = self.get_order_part(order_by)
        if not is_null_or_empty(orderf):
            ret += ' order by {0}'.format(orderf)
        print(ret)
        if is_null_or_empty(self.plus):
            return self.database.connection.execute(ret)
        else:
            return self.database.connection.execute(ret, self.plus)
    
    def get_from_part(self):
        ret = "deals_view d inner join selected_stocks s on s.stock = d.security_name"
        if self.dialog.account_current.get_value() == "select":
            ret += " inner join selected_accounts a on d.account_id = a.account_id"
        return ret
            
    def get_order_part(self, orderfield):
        return u'd.{0}'.format(orderfield)
        
        
        
        
    def _regen_selected(self):
        if not self.database.connection:
            return
        self.database.set_selected_stocks(map(lambda a: a[0], self.dialog.instruments.get_checked_rows()))
        if self.dialog.account_current.get_value() == "current":
            (name, ) = self.database.connection.execute("select name from accounts where id = ?", (gethash(self.global_data, "current_account"), )).fetchone() or (None, )
            self.database.set_selected_accounts(name != None and [name] or None)
        elif self.dialog.account_current.get_value() == "select":
            self.database.set_selected_accounts(map(lambda a: a[0], self.dialog.accounts.get_checked_rows()))

    
    def __init__(self, global_data, builder, database):
        self.builder = builder
        self.database = database
        self.global_data = global_data
        self.dialog = deals_filter_control(builder)

    def _prepare_filter(self):
        if self.database.connection:
            sl = map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals"))
            also = {}
            for (key, val) in [("count_range", "quantity"),
                               ("price_range", "price"),
                               ("broker_comm_range", "broker_comm"),
                               ("stock_comm_range", "stock_comm"),
                               ("comm_range", "broker_comm + stock_comm"),
                               ("volume_range", "volume")]:
                also[key] = self.database.connection.execute("select min({0}), max({0}) from deals".format(val)).fetchone()
            also["stock_list"] = sl
            also["accounts_list"] = map(lambda a: a[0], self.database.connection.execute("select distinct name from accounts order by name"))
            self.dialog.update_widget(**also)

    def get_where_part(self, parent):
        
        conds = []
        def lower_upper(field_name, l, h):
            if l and h:
                if l < h:
                    conds.append(u'({0} between ? and ?)'.format(field_name))
                    self.plus += [l, h]
                elif l > h:
                    conds.append(u'({0} >= ? or {0} <= ?)'.format(field_name))
                    self.plus += [l, h]
                else:
                    conds.append(u'{0} = ?'.format(field_name))
                    self.plus.append(l)
            elif l:
                conds.append(u'{0} >= ?'.format(field_name))
                self.plus.append(l)
            elif h:
                conds.append(u'{0} <= ?'.format(field_name))
                self.plus.append(h)
            
        #################
        # number ranges #
        #################
        for (control, field_name) in [(self.dialog.count, "d.quantity"),
                                      (self.dialog.price, "d.price"),
                                      (self.dialog.broker_comm, "d.broker_comm"),
                                      (self.dialog.stock_comm, "d.stock_comm"),
                                      (self.dialog.comm, "d.comm"),
                                      (self.dialog.volume, "d.volume")]:
            lower_upper(field_name, control.get_lower_value(), control.get_upper_value())

        #################
        # date controls #
        #################
        ld = self.dialog.datetime_range.get_lower_datetime()
        hd = self.dialog.datetime_range.get_upper_datetime()
        lower_upper("d.datetime", ld, hd)

        ####################
        # select controls  #
        ####################
        pp = self.dialog.position.get_value()
        if pp != None:
            if pp:
                conds.append(u'd.position_id is null')
            else:
                conds.append(u'd.position_id is not null')

        dd = self.dialog.direction.get_value()
        if dd != None:
            lower_upper("d.deal_sign", dd, dd)

        if (gethash(self.global_data, "current_account") == None and self.dialog.account_current.get_value() == "current") or self.dialog.account_current.get_value() == "none":
            conds.append("d.account_id is null")
        elif self.dialog.account_current.get_value() == "current":
            lower_upper("d.account_id", self.global_data["current_account"], self.global_data["current_account"])
        if parent != None:
            lower_upper("d.parent_deal_id", parent, parent)

        return len(conds) > 0 and reduce_by_string(' and ', conds) or None
            
        

