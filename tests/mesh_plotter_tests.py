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
        self.assertEqual([datetime(2002, 3, 6), datetime(2002, 3, 7), datetime(2002, 3, 8)],
                         self.obj._generate_times(datetime(2002, 3, 5, 17, 40), datetime(2002, 3, 8, 2, 58, 3), 3600 * 24))
        self.assertEqual([datetime(2004, 6, 3), datetime(2004, 6, 3, 0, 30), datetime(2004, 6, 3, 1, 0)],
                         self.obj._generate_times(datetime(2004, 6, 2, 23, 40), datetime(2004, 6, 3, 1, 0), 30 * 60))
        


if __name__ == '__main__':
    unittest.main()
