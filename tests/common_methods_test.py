#!/bin/env python
# -*- coding: utf-8 -*-
## common_methods_test ##


import unittest
from common_methods import *


class cm_test(unittest.TestCase):
    """Testing some methods in common_methods module
    Attributes:
    
    """
    def test_where_format(self, ):
        """format_where_part tester
        """
        (string, args) = format_where_part([(">=", ["some_field"], 10), ("between", ["value"], 100, 200)])
        self.assertTrue(len(string) > 0)
        self.assertEqual([10, 100, 200], args)
        print("Where part of query is {0}".format(string))
        
