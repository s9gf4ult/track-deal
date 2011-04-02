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

    def fill_model(self, model, sort_field):
        self._prepare_filter()          # это чтобы стоки попали в фильтр
    
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
                also[key] = self.database.connection.execute("select min({0}), max({0}) from deals".format(val)).fetchone()
            also["stock_list"] = sl
            self.dialog.update_widget(**also)

    def _gen_bounadary_conditions(self, deals_alias):
        conds = []
        
        def aliased(field_name):
            if deals_alias != None and len(deals_alias) > 0:
                return u'{0}.{1}'.format(deals_alias, field_name)
            else:
                return field_name

        def lower_upper(field_name, l, h):
            if l and h:
                if l < h:
                    conds.append(u'({0} between {1} and {2})'.format(field_name, l, h))
                elif l > h:
                    conds.append(u'({0} >= {1} or {0} <= {2}'.format(field_name, l, h))
                else:
                    conds.append(u'{0} = {1}'.format(field_name, l))
            elif l:
                conds.append(u'{0} >= {1}'.format(field_name, l))
            elif h:
                conds.append(u'{0} <= {1}'.format(field_name, h))
            
        #################
        # number ranges #
        #################
        for (control, field_name) in [(self.dialog.count, aliased("quantity")),
                                      (self.dialog.price, aliased("price")),
                                      (self.dialog.broker_comm, aliased("broker_com")),
                                      (self.dialog.stock_comm, aliased("stock_comm")),
                                      (self.dialog.comm, u'{0} + {1}'.format(aliased("broker_comm"), aliased("stock_comm"))),
                                      (self.dialog.volume, aliased("volume"))]:
            lower_upper(field_name, control.get_lower_value(), control.get_upper_value())

        #################
        # date controls #
        #################
        ld = self.dialog.datetime_range.get_lower_datetime()
        hd = self.dialog.datetime_range.get_upper_datetime()
        lower_upper("datetime", ld, hd)

        ####################
        # select controls  #
        ####################
        pp = self.dialog.position.get_value()
        if pp != None:
            if pp:
                conds.append(u'position_id is not null')
            else:
                conds.append(u'position_id is null')

        dd = self.dialog.direction.get_value()
        if dd != None:
            conds.append(u'deal_sign = {0}'.format(dd))

        return reduce(lambda a, b: u'{0} and {1}'.format(a, b), conds)
            
        

