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
        (a, b) = format_where_part([("<=", ["a"], ["b"]), ("=", ["soso"], ["ruru"])], "or")
        self.assertEqual([], b)
        self.assertEqual("a <= b or soso = ruru", a)
        (x, y) = format_where_part([("=", ["fof"], None), ("<>", ["fufu"], None)])
        self.assertEqual("fof is null and fufu is not null", x)
        self.assertEqual([], y)
        
        
if __name__ == '__main__':
    unittest.main()
