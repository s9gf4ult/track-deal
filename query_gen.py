#!/bin/env python
# -*- coding: utf-8 -*-

class query_gen():
    """class to generate queries to the database"""
    in_work = False
    returnings = []
    conditions = []
    force_joins = []
    """list of aliases to force join tables"""
    tables = []
    joins = []
    
    def __init__(self, tables, joins):
        """tables is a list of tuples [(table_name, alias)], joins is a hash table like that {"=" : [((alias, field), (alias, field))], ">" : [((alias, field), (alias, field))]}"""
        self.tables = tables
        self.joins = joins

    def begin(self):
        self.in_work = True

    def add_returner(self, returners):
        """returners is a list of tuples like that [(alias, field)... ], adds to the query field to get from"""
        self.check_working()
        aliases = map(lambda a: a[1], self.tables)
        for rt in returners:
            if rt not in aliases:
                raise Exception("There is no alias {0} to return field from".format(rt))
        self.returnings += returners

    def check_working(self):
        if not self.in_work:
            raise Exception("query not in work generation")

    def add_force_joins(self, aliases):
        als = map(lambda a: a[1], self.tables)
        for al in aliases:
            if al not in als:
                raise Exception("There is no alias {0} to force join".format(al))
        self.force_joins += aliases
                                
