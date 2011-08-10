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
    ## string with name of report type
    report_type = ""
    ## type of 'open.ru' report, 'tuture' or 'stock'
    open_ru_report_type = ''
    ## int to describe the count of deals in the report
    deals_count = -1
    ## int - count of positions
    positions_count = -1

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

    def make_money_and_account(self, ):
        """\return
        (int, int) - money and account id
        """
        mid = self.model.create_money('RU', 'Russian rubles')
        aid = self.model.create_account('test', mid, 10000)
        return (mid, aid)

    
    def test_preliminary(self, ):
        """
        \brief test of deals count, type of the report, type of the papers
        """
        (mid, aid) = self.make_money_and_account()
        self.model.load_from_source(aid, self.source)
        if self.deals_count >= 0:
            self.assertEqual(self.deals_count, self.model._sqlite_connection.execute('select count(*) from deals').fetchone()[0])
            print('deals count passed')
        if self.report_type == 'open.ru':
            self.assertTrue(isinstance(self.source, sources.open_ru_report_source))
            if self.open_ru_report_type == 'stock':
                pt = self.model.get_paper_type('stock')
                self.assertEqual(set([pt['id']]), set(map(lambda a: a[0], self.model._sqlite_connection.execute('select distinct type from papers').fetchall())))
                print('stock or fut passed')
            elif self.open_ru_report_type == 'future':
                pt = self.model.get_paper_type('future')
                self.assertEqual(set([pt['id']]), set(map(lambda a: a[0], self.model._sqlite_connection.execute('select distinct type from papers').fetchall())))
                print('stock or fut passed')

    def test_positions_count(self, ):
        (mid, aid) = self.make_money_and_account()
        self.model.load_from_source(aid, self.source)
        if self.positions_count >= 0:
            self.model.make_positions_for_whole_account(aid)
            self.assertEqual(self.positions_count, self.model._sqlite_connection.execute('select count(*) from positions').fetchone()[0])
            print('positions count passed')

    def test_open_ru_fut_commission(self, ):
        """\brief test commission calculating right for futures
        """
        if self.report_type == 'open.ru' and self.open_ru_report_type == 'future':
            (mid, aid) = self.make_money_and_account()
            self.model.load_from_source(aid, self.source)
            ta = self.source.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
            comm = reduce(lambda a, b: abs(float(a.attributes['total_value'].nodeValue)) +
                          abs(float(b.attributes['total_value'].nodeValue)),
                          filter(lambda c: c.attributes['total_description'].nodeValue in (u'Вознаграждение Брокера', u'Биржевой сбор'), ta))
            self.assertAlmostEqual(comm, self.model._sqlite_connection.execute('select sum(commission) from deals').fetchone()[0])
            print('open.ru commission for futures passed')

    def test_open_ru_stock_commission(self, ):
        """\brief test commission ballance for open.ru reports
        """
        if self.report_type == 'open.ru' and self.open_ru_report_type == 'stock':
            (mid, aid) = self.make_money_and_account()
            self.model.load_from_source(aid, self.source)
            cd = self.source.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
            comm = reduce(lambda a, b: a + b,
                          map(lambda c: float(c.attributes['broker_comm'].nodeValue) + float(c.attributes['stock_comm'].nodeValue),
                              cd))
            self.assertAlmostEqual(comm, self.model._sqlite_connection.execute('select sum(commission) from deals').fetchone()[0])
            print('test stock commission passed')

    def test_open_ru_ballance(self, ):
        """\brief check if ballance for deals matches for report and database
        """
        if self.report_type == 'open.ru':
            (mid, aid) = self.make_money_and_account()
            self.model.load_from_source(aid, self.source)
            cd = self.source.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
            if self.open_ru_report_type == 'stock':
                comm = reduce(lambda a, b: a + b,
                              map(lambda c: float(c.attributes['broker_comm'].nodeValue) + float(c.attributes['stock_comm'].nodeValue),
                                  cd))
            elif self.open_ru_report_type == 'future':
                ta = self.source.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
                comm = reduce(lambda a, b: abs(float(a.attributes['total_value'].nodeValue)) +
                              abs(float(b.attributes['total_value'].nodeValue)),
                              filter(lambda c: c.attributes['total_description'].nodeValue in (u'Вознаграждение Брокера', u'Биржевой сбор'), ta))

            ballance = reduce(lambda a, b: a + b,
                              map(lambda c: float(c.attributes['deal_sign'].nodeValue) *
                                  float(c.attributes['price'].nodeValue) *
                                  float(c.attributes['quantity'].nodeValue), cd)) - comm + 10000 # 10000 is the initial money
            accs = self.model.list_view_accounts().fetchall()
            self.assertEqual(1, len(accs))
            self.assertAlmostEqual(ballance, accs[0]['current_money'])

    def test_open_ru_ballance_after_make_position(self, ):
        """\brief test if make position does not change the ballance of account
        """
        (mid, aid) = self.make_money_and_account()
        self.model.load_from_source(aid, self.source)
        accs = self.model.list_view_accounts().fetchall()
        self.assertEqual(1, len(accs))
        before = accs[0]['current_money']
        self.model.tamake_positions_for_whole_account(aid)
        accs = self.model.list_view_accounts().fetchall()
        after = accs[0]['current_money']
        self.assertAlmostEqual(before, after)
    

                

class import_report1(import_report):
    """\brief class to open 'test_report1.xml'
    """
    filename = 'tests/test_report1.xml'
    report_type = 'open.ru'
    open_ru_report_type = 'stock'
    deals_count = 5
    positions_count = 2
    
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report2(import_report):
    """\brief class to open 'test_report2.xml'
    """
    filename = 'tests/test_report2.xml'
    report_type = 'open.ru'
    open_ru_report_type = 'stock'
    deals_count = 8
    positions_count = 4
    
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report3(import_report):
    """\brief class to open 'test_report3.xml'
    """
    filename = 'tests/test_report3.xml'
    report_type = 'open.ru'
    open_ru_report_type = 'future'
    deals_count = 19
    def open_file(self, ):
        self.source = sources.open_ru_report_source()
        self.source.open(self.filename)
        
class import_report4(import_report):
    """\brief class to open 'test_report4.xml'
    """
    filename = 'tests/test_report4.xml'
    report_type = 'open.ru'
    open_ru_report_type = 'stock'
    deals_count = 18
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
