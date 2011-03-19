#/bin/env python
# -*- coding: utf-8 -*-
from deals_filter_dialog import deals_filter_dialog

class deals_filter():
    def __init__(self, database, parent = None, modal = True, dialog = None, update_action = None):
        self.database = database
        if dialog:
            self.dialog = dialog
        else:
            self.dialog = deals_filter_dialog(parent = parent, modal = modal, update_action = update_action)

    def _prepare_filter(self):
        if self.database.connection:
            sl = map(lambda a: a[0], self.database.connection.execute("select distinct security_name from deals").fetchall())
            self.deals_filter.update_widget(stock_list = sl, min_max_price = self.database.connection.execute("select min(price), max(price) from deals").fetchone(),
                                            min_max_count = self.database.connection.execute("select min(quantity), max(quantity) from deals").fetchone(),
                                            min_max_commission = self.database.connection.execute("select min(broker_comm + stock_comm), max(broker_comm + stock_comm) from deals").fetchone())

        
    def pick_up_filter_condition(self):
        ret = "";
        self.database.connection.execute("delete from selected_stocks")
        it = self.deals_filter.stock_check.list_store.get_iter_first()
        while it:
            if self.deals_filter.stock_check.list_store.get_value(it, 0):
                self.database._insert_from_hash("selected_stocks", {"stock" : self.deals_filter.stock_check.list_store.get_value(it, 1)})
            it = self.deals_filter.stock_check.list_store.iter_next(it)
        pos_val = self.deals_filter.is_position.get_selected()
        if pos_val != None:
            if pos_val:
                ret += " and d.position_id is not null"
            else:
                ret += " and d.position_id is null"

        dir_val = self.deals_filter.direction.get_selected()
        if dir_val != None:
            ret += " and d.deal_sign == {0}".format(dir_val)
            print(dir_val)

        price_from = self.deals_filter.price_range.get_from_integer()
        if price_from:
            ret += " and d.price >= {0}".format(price_from)
            print(price_from)

        price_to = self.deals_filter.price_range.get_to_integer()
        if price_to:
            ret += " and d.price <= {0}".format(price_to)
            print(price_to)

        count_from = self.deals_filter.count_range.get_from_integer()
        if count_from:
            ret += " and d.quantity >= {0}".format(count_from)

        count_to = self.deals_filter.count_range.get_to_integer()
        if count_to:
            ret += " and d.quantity <= {0}".format(count_to)

        comm_from = self.deals_filter.commission.get_from_integer()
        if comm_from:
            ret += " and (d.broker_comm + d.stock_comm) >= {0}".format(comm_from)

        comm_to = self.deals_filter.commission.get_to_integer()
        if comm_to:
            ret += " and (d.broker_comm + d.stock_comm) <= {0}".format(comm_to)

        date_from = self.deals_filter.date_selector.get_datetime_from()
        if date_from:
            ret += " and d.datetime >= {0}".format(time.mktime(date_from.timetuple()))
            print(date_from)

        date_to = self.deals_filter.date_selector.get_datetime_to()
        if date_to:
            ret += " and d.datetime <= {0}".format(time.mktime(date_to.timetuple()))
            print(date_to)
            
        return ret


