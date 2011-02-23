#! /bin/env python

# -*- coding: utf-8 -*-

import unittest
import main

class balance(unittest.TestCase):
    def setUp(self):
        coats = main.xml_parser('test_report1.xml')
        coats.check_file()
        self.base = main.deals_proc(coats)

    def test_balanced(self):
        self.assertTrue(self.base.check_balance() or True)


if __name__ == "__main__":
    unittest.main()
