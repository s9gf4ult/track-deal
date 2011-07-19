#! /bin/env python
# -*- coding: utf-8 -*-

import unittest
import sources
import random
from sqlite_model import sqlite_model

class import_report(unittest.TestCase):
    """\brief common class for testing the report import
    """
    ## string with file name to load data from
    filename = ""

    ## int to describe the count of deals in the report
    deals_count = 0

    def setUp(self, ):
        """\brief initial setup for test
        """
        self.open_file()
        self.model = sqlite_model()
        self.model.create_new(':memory:')

    def open_file(self, ):
        """\brief open file and set 'source' property of the self
        """
        raise NotImplementedError()

    def test_dummy(self, ):
        self.assertTrue(True)




class import_report1(import_report):
    """\brief class to open 'test_report1.xml'
    """
    filename = 'tests/test_report1.xml'
    deals_count = 5
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report2(import_report):
    """\brief class to open 'test_report2.xml'
    """
    filename = 'tests/test_report2.xml'
    deals_count = 5
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report3(import_report):
    """\brief class to open 'test_report3.xml'
    """
    filename = 'tests/test_report3.xml'
    deals_count = 5
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report4(import_report):
    """\brief class to open 'test_report4.xml'
    """
    filename = 'tests/test_report4.xml'
    deals_count = 5
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        

    
if __name__ == "__main__":
    for test_case in [import_report1,
                      import_report2,
                      import_report3,
                      import_report4]:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
