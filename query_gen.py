#!/bin/env python
# -*- coding: utf-8 -*-

class query_gen():
    """class to generate queries to the database"""
    in_work = False
    returnings = []
    conditions = ["and"]
    force_joins = []
    """list of aliases to force join tables"""
    tables = []
    joins = []
    
    def __init__(self, tables, joins):
        """tables is a list of tuples [(table_name, alias)], joins is a hash table like that [("="  ((alias, field), (alias, field))), (">" : ((alias, field), (alias, field)))]"""
        self.tables = tables
        self.joins = joins

    def begin(self):
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
        self.conditions += conditions
        
    def end(self):
        rets = reduce(lambda a, b: u'{0}, {1}'.format(a, b),
                      map(lambda x: u'{0}.{1}'.format(*x), self.returnings))
        jtables = sorted(set(map(lambda a: a[0], self.returnings) + self.force_joins + self.get_tables_from_conditions()))
        return u'select {0} from {1} where {2}

    def get_tables_from_conditions(self):
        return self._get_tables_from_conditions(self.conditions)

    def _get_tables_from_conditions(self, conditions):
        if not isinstance(conditions, list):
            raise Exception("conditions must start from list")
        if conditions[0] not in ["and", "or"]:
            raise Exception("conditions must start from 'and' or 'or'")
        
