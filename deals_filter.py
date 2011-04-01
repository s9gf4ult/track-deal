#/bin/env python
# -*- coding: utf-8 -*-
from deals_filter_dialog import deals_filter_dialog
import time


class iter_filter():
    def __init__(self, cursor):
        self.cursor = cursor

    def next(self):
        return self.cursor.next()[0]

class cursor_filter():
    def __init__(self, query, connection):
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
        return self.dialog.run()

    def get_ids(self, order_by, parent = None):
        if self.database.connection:
            q = self.get_ids_query(order_by, parent)
            return cursor_filter(q, self.database.connection)
        else:
            return cursor_empty()
    
    def __init__(self, builder, database):
        self.builder = builder
        self.database = database
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
                also[key] = self.database.connection.execute("select min({0}), max({0}) from deals".format(val))
            also["stock_list"] = sl
            self.dialog.update_widget(**also)

        
    def get_ids_query(self, order_by, parent = None):
        ret = "select d.id from deals d inner join selected_stocks s on d.security_name = s.stock where " + (parent == None and "d.parent_deal_id is null" or "d.parent_deal_id = {0}".format(parent))
        lasttc = self.database.connection.total_changes
        self.database.connection.execute("delete from selected_stocks")
        it = self.dialog.stock_check.list_store.get_iter_first()
        while it:
            if self.dialog.stock_check.list_store.get_value(it, 0):
                self.database._insert_from_hash("selected_stocks", {"stock" : self.dialog.stock_check.list_store.get_value(it, 1)})
            it = self.dialog.stock_check.list_store.iter_next(it)
        self.database.last_total_changes += self.database.connection.total_changes - lasttc
        
        pos_val = self.dialog.is_position.get_selected()
        if pos_val != None:
            if pos_val:
                ret += " and d.position_id is not null"
            else:
                ret += " and d.position_id is null"

        dir_val = self.dialog.direction.get_selected()
        if dir_val != None:
            ret += " and d.deal_sign == {0}".format(dir_val)
            print(dir_val)
            
        date_from = self.dialog.date_selector.get_datetime_from()
        date_to = self.dialog.date_selector.get_datetime_to()

        for (ifrom, ito, field) in [(self.dialog.price_range.get_from_integer(),
                                     self.dialog.price_range.get_to_integer(), "d.price"),
                                    (self.dialog.count_range.get_from_integer(),
                                     self.dialog.count_range.get_to_integer(), "d.quantity"),
                                    (self.dialog.commission.get_from_integer(),
                                     self.dialog.commission.get_to_integer(), "(d.broker_comm + d.stock_comm)"),
                                    (date_from and time.mktime(date_from.timetuple()),
                                     date_to and time.mktime(date_to.timetuple()), "d.datetime")]:
            if ifrom and ito:
                if ifrom < ito:
                    ret += " and {0} between {1} and {2}".format(field, ifrom, ito)
                elif ifrom > ito:
                    ret += " and ({0} >= {1} or {0} <= {2})".format(field, ifrom, ito)
                else:
                    ret += " and {0} = {1}".format(field, ifrom)
            elif ifrom:
                ret += " and {0} >= {1}".format(field, ifrom)
            elif ito:
                ret += " and {0} <= {1}".format(field, ito)

        if order_by and order_by != "":
            ret += " order by d.{0}".format(order_by)
                             
        return ret


