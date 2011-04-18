#!/bin/env python
# -*- coding: utf-8 -*-

class query_gen():
    in_work = False
    returnings = []
    conditions = []
    
    def __init__(self, tables, joins):
        """tables is a list of tuples [(table_name, alias)], joins is a hash table like that {"=" : [((alias, field), (alias, field))], ">" : [((alias, field), (alias, field))]}"""
        self.tables = tables
        self.joins = joins
