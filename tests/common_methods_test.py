#!/bin/env python
# -*- coding: utf-8 -*-
## common_methods_test ##


import unittest
from common_methods import *


class cm_test(unittest.TestCase):
    """Testing some methods in common_methods module
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

    def test_get_next_month_date(self, ):
        self.assertEqual(datetime.datetime(2010, 1, 1), get_next_month_date(datetime.datetime(2009, 12, 1)))
        self.assertEqual(datetime.datetime(2020, 5, 20), get_next_month_date(datetime.datetime(2020, 4, 20)))

    def test_years_range(self, ):
        self.assertEqual(1, years_range(datetime.datetime(2010, 1, 1), datetime.datetime(2011, 1, 1)))
        self.assertEqual(0, years_range(datetime.datetime(2010, 1, 6), datetime.datetime(2011, 1, 1)))
        self.assertEqual(0, years_range(datetime.datetime(2000, 4, 8), datetime.datetime(2001, 4, 7)))
        self.assertEqual(5, years_range(datetime.datetime(2000, 3, 20), datetime.datetime(2005, 8, 22)))

    def test_months_range(self, ):
        self.assertEqual(1, months_range(datetime.datetime(2000, 3, 1), datetime.datetime(2000, 4, 1)))
        self.assertEqual(0, months_range(datetime.datetime(2000, 3, 6), datetime.datetime(2000, 4, 9)))
        self.assertEqual(1, months_range(datetime.datetime(2000, 3, 6), datetime.datetime(2000, 5, 9)))
        self.assertEqual(12, months_range(datetime.datetime(2000, 1, 1), datetime.datetime(2001, 1, 1)))
        self.assertEqual(12, months_range(datetime.datetime(2008, 3, 6), datetime.datetime(2009, 4, 9)))
        self.assertEqual(24, months_range(datetime.datetime(2004, 3, 1), datetime.datetime(2006, 3, 1)))
        self.assertEqual(24 - 1, months_range(datetime.datetime(2004, 3, 8), datetime.datetime(2006, 3, 8)))
        self.assertEqual(7, months_range(datetime.datetime(2004, 4, 8), datetime.datetime(2004, 12, 31)))

    def test_color_string_to_tuple(self, ):
        self.assertEqual((1, 0, 0), color_string_to_tuple('#FF0000'))
        self.assertEqual((0, 1, 0), color_string_to_tuple('#00FF00'))
        self.assertEqual((0, 0, 1), color_string_to_tuple('#0000FF'))

    def test_is_blank(self, ):
        self.assertEqual(True, is_blank('   '))
        self.assertEqual(True, is_blank(''))
        self.assertEqual(False, is_blank('   3   '))

if __name__ == '__main__':
    unittest.main()
