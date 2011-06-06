#!/bin/env python
# -*- coding: utf-8 -*-

from common_methods import *

class query_gen():
    """class to generate queries to the database"""
    in_work = False
    returnings = []
    conditions = ["and"]
    force_joins = []
    group_bys = []
    order_bys = []
    """list of aliases to force join tables"""
    tables = []
    left_joins = []
    inner_joins = []
    outer_joins = []
    
    def __init__(self, tables, inner_joins = [], left_joins = [], outer_joins = []):
        """tables is a list of tuples [(table_name, alias)], joins is a list like that [("="  (alias, field), (alias, field)), (">" : (alias, field), (alias, field))]"""
        self.tables = tables
        self.left_joins
        self.inner_joins = inner_joins
        self.outer_joins = outer_joins

    def begin(self):
        if self.in_work == True:
            raise Exception("query gen: Already in work")
        self.in_work = True

    def add_returners(self, returners):
        """returners is a list of tuples like that [(alias, field)... ], adds to the query field to get from"""
        self.check_working()
        aliases = map(lambda a: a[1], self.tables)
        for rt in returners:
            if rt[0] not in aliases:
                raise Exception("There is no alias {0} to return field from".format(rt[0]))
        self.returnings += returners

    def check_working(self):
        if not self.in_work:
            raise Exception("query not in work generation")

    def add_force_joins(self, aliases):
        self.check_working()
        als = map(lambda a: a[1], self.tables)
        for al in aliases:
            if al not in als:
                raise Exception("There is no alias {0} to force join".format(al))
        self.force_joins += aliases

    def add_conditions(self, conditions):
        """conditions is a list like that ["and" ((alias, field), "=", (alias2, field2)), ((alias3, field3), ">", (alias4, field4)), ((alis5, field5), "between", 10, "and", 20)]"""
        self.check_working()
        self.conditions.append(conditions)
        
    def end(self):
        # rets = reduce(lambda a, b: u'{0}, {1}'.format(a, b),
        #               map(lambda x: u'{0}.{1}'.format(*x), self.returnings))
        # jtables = sorted(set(map(lambda a: a[0], self.returnings) + self.force_joins + self.get_tables_from_conditions()))
        ret = u'select {0} from {1}'.format(self.get_select_part(), self.get_from_part())
        wh = self.get_where_part()
        if wh != None:
            ret += u' where {0}'.format(wh)
        grpb = self.get_group_by_part()
        if grpb != None:
            ret += u' group by {0}'.format(grpb)
        ordb = self.get_order_by_part()
        if ordb != None:
            ret += u' order by {0}'.format(ordb)
        self.force_joins = []
        self.conditions = ["and"]
        self.returnings = []
        self.in_work = False
        return ret

    def _tuple_to_datatext(self, dtuple):
        return u'{0}.{1}'.format(*dtuple[:2])

    def get_select_part(self):
        ret = reduce_by_string(", ", map(self._tuple_to_datatext,
                                         self.returnings))
        return ret
        

    def get_from_part(self):
        return ""

    def get_where_part(self):
        return None

    def get_order_by_part(self):
        return None

    def get_group_by_part(self):
        return None
        

    def get_tables_from_conditions(self):
        return self._get_tables_from_conditions(self.conditions)

    def _get_tables_from_conditions(self, conditions):
        if is_null_or_empty(conditions):
            return []
        if not isinstance(conditions, list):
            raise Exception("conditions must start from list")
        if conditions[0] not in ["and", "or"]:
            raise Exception("conditions must start from 'and' or 'or'")
        
        def get_tablenames_from_tuple(obj):
            return reduce(lambda a, b: a + b,
                          map(lambda x: isinstance(x, tuple) and [x[0]] or [],
                              obj))
        
        def get_table_names(obj):
            if isinstance(obj, list):
                return self._get_tables_from_conditions(obj)
            elif isinstance(obj, tuple):
                return get_tablenames_from_tuple(obj)
            else:
                raise Exception("{0} must be tuple or list at all".format(obj))
            
        if is_null_or_empty(conditions[1:]):
            return []
        return reduce(lambda a, b: a + b,
                      map(get_table_names, conditions[1:]))
        
