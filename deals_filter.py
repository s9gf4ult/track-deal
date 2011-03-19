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
    def __init__(self):
        pass
    def __iter__(self):
        return empty_iter()

class empry_iter():
    def __init__(self):
        pass
    def next():
        raise StopIteration()

class deals_filter():

    def show(self):
        self.dialog.show()

    def get_ids(self, order_by):
        if self.database.connection:
            self._prepare_filter()
            q = self.get_ids_query(order_by)
            return cursor_filter(q, self.database.connection)
        else:
            return cursor_empty()
    
    def __init__(self, database, parent = None, modal = True, dialog = None, update_action = None):
        self.database = database
        if dialog:
            self.dialog = dialog
        else:
            self.dialog = deals_filter_dialog(parent = parent, modal = modal, update_action = update_action)

    def _prepare_filter(self):
        if self.database.connection:
            sl = map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals").fetchall())
            self.dialog.update_widget(stock_list = sl,
                                      min_max_price = self.database.connection.execute("select min(price), max(price) from deals").fetchone(),
                                      min_max_count = self.database.connection.execute("select min(quantity), max(quantity) from deals").fetchone(),
                                      min_max_commission = self.database.connection.execute("select min(broker_comm + stock_comm), max(broker_comm + stock_comm) from deals").fetchone())

        
    def get_ids_query(self, order_by):
        ret = "select d.id from deals d inner join selected_stocks s on d.security_name = s.stock where d.parent_deal_id is null"
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


