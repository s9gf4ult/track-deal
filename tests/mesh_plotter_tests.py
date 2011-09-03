#!/bin/env python
# -*- coding: utf-8 -*-
## mesh_plotter_tests ##

import unittest
from mesh_plotter import mesh_plotter
from datetime import datetime

class mesh_plotter_tests(unittest.TestCase):

    def setUp(self, ):
        self.obj = mesh_plotter()
        self.maxDiff = None

    def test_generate_times(self, ):
        """\brief _generate_times method test
        """
        self.assertEqual([datetime(2010, 10, 1, 12, 0), datetime(2010, 10, 1, 12, 5)],
                         self.obj._generate_times(datetime(2010, 10, 1, 11, 59), datetime(2010, 10, 1, 12, 7), 5 * 60))
        
        self.assertEqual([],
                         self.obj._generate_times(datetime(2010, 10, 1, 12, 1), datetime(2010, 10, 1, 12, 0, 2), 3))
        
        self.assertEqual([datetime(2004, 6, 3), datetime(2004, 6, 3, 0, 30), datetime(2004, 6, 3, 1, 0)],
                         self.obj._generate_times(datetime(2004, 6, 2, 23, 40), datetime(2004, 6, 3, 1, 0), 30 * 60))

        self.assertEqual([datetime(2003, 4, 4, 4, 0), datetime(2003, 4, 4, 5, 0)],
                         self.obj._generate_times(datetime(2003, 4, 4, 3, 12), datetime(2003, 4, 4, 5, 55), 3600))

        self.assertEqual([datetime(2000, 5, 5, 12, 0), datetime(2000, 5, 6, 0, 0), datetime(2000, 5, 6, 12, 0)],
                         self.obj._generate_times(datetime(2000, 5, 5, 8, 33), datetime(2000, 5, 6, 15, 10), 3600 * 12))
        
        
    def test_generate_months(self, ):
        """\brief _generate_months test
        """
        self.assertEqual([datetime(2004, 11, 1), datetime(2004, 12, 1)],
                         self.obj._generate_months(datetime(2004, 10, 3, 4, 9), datetime(2004, 12, 4, 22, 44)))
        self.assertEqual([datetime(2000, 12, 1), datetime(2001, 1, 1), datetime(2001, 2, 1), datetime(2001, 3, 1)],
                         self.obj._generate_months(datetime(2000, 11, 5), datetime(2001, 3, 23)))

    def test_generate_days(self, ):
        """\brief  _generate_days
        """
        self.assertEqual([datetime(2001, 3, 6), datetime(2001, 3, 7)],
                         self.obj._generate_days(datetime(2001, 3, 5, 2, 1), datetime(2001, 3, 7, 0, 0)))
        self.assertEqual([datetime(2001, 3, 5), datetime(2001, 3, 6), datetime(2001, 3, 7)],
                         self.obj._generate_days(datetime(2001, 3, 5, 0, 0), datetime(2001, 3, 7, 5, 3)))



if __name__ == '__main__':
    unittest.main()
