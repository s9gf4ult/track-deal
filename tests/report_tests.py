#! /bin/env python
# -*- coding: utf-8 -*-

from loaders.open_ru.open_ru_loader import open_ru_loader
from loaders.open_ru.open_ru_source import open_ru_source
from sqlite_model import sqlite_model
from xml.dom import minidom
import unittest

class import_report(unittest.TestCase):
    """\brief common class for testing the report import
    """

    def __init__(self, *args, **kargs):
        super(import_report, self).__init__(*args, **kargs)
        ## string with file name to load data from
        self.filename = ""
        ## string with name of report type
        self.report_type = ""
        ## type of 'open.ru' report, 'tuture' or 'stock'
        self.open_ru_report_type = ''
        ## int to describe the count of deals in the report
        self.deals_count = -1
        ## int - count of positions
        self.positions_count = -1

    def setUp(self):
        """\brief initial setup for test
        """
        self.model = sqlite_model()
        self.model.create_new(':memory:')

    def load_data_into_account(self, account_id):
        '''must be implemented in children
        \param account_id
        '''
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
        (mid, aid) = self.make_money_and_account() #@UnusedVariable
        self.load_data_into_account(aid)
        if self.deals_count >= 0:
            self.assertEqual(self.deals_count, self.model._sqlite_connection.execute('select count(*) from deals').fetchone()[0])
            print('deals count passed')
        if self.report_type == 'open.ru':
            if self.open_ru_report_type == 'stock':
                pt = self.model.get_paper_type('stock')
                self.assertEqual(set([pt['id']]), set(map(lambda a: a[0], self.model._sqlite_connection.execute('select distinct type from papers').fetchall())))
                print('stock or fut passed')
            elif self.open_ru_report_type == 'future':
                pt = self.model.get_paper_type('future')
                self.assertEqual(set([pt['id']]), set(map(lambda a: a[0], self.model._sqlite_connection.execute('select distinct type from papers').fetchall())))
                print('stock or fut passed')

    def test_positions_count(self, ):
        (mid, aid) = self.make_money_and_account() #@UnusedVariable
        self.load_data_into_account(aid)
        if self.positions_count >= 0:
            self.model.make_positions_for_whole_account(aid)
            self.assertEqual(self.positions_count, self.model._sqlite_connection.execute('select count(*) from positions').fetchone()[0])
            print('positions count passed')



    def get_open_ru_parsed(self):
        parsed = minidom.parse(self.filename)
        report = parsed.getElementsByTagName('report')[0]
        return report

    def get_account_totally_line(self):
        report = self.get_open_ru_parsed()
        atlt = report.getElementsByTagName('account_totally_line')[0]
        ret = atlt.getElementsByTagName('item')
        return ret
    

    def open_ru_get_forts_comm(self, atl):
        filtered_atl = filter(lambda x:x.getAttribute('total_description') in [u'Вознаграждение Брокера', u'Биржевой сбор'], atl)
        summcomm = sum([abs(float(x.getAttribute('total_value'))) for x in filtered_atl])
        return summcomm

    def test_open_ru_fut_commission(self, ):
        """\brief test commission calculating right for futures
        """
        if self.report_type == 'open.ru' and self.open_ru_report_type == 'future':
            (mid, aid) = self.make_money_and_account() #@UnusedVariable
            self.load_data_into_account(aid)
            atl = self.get_account_totally_line()
            if len(atl) == 0:
                return
            summcomm = self.open_ru_get_forts_comm(atl)
            self.assertAlmostEqual(summcomm,
                                   sum([d['commission'] for d in self.model.list_deals(aid)]))
            print('open.ru commission for futures passed')


    def get_deals(self):
        report = self.get_open_ru_parsed()
        deals = report.getElementsByTagName('common_deal')[0]
        ret = deals.getElementsByTagName('item')
        return ret
    
    def get_repo_deals(self):
        report = self.get_open_ru_parsed()
        repos = report.getElementsByTagName('repo_deal')
        if len(repos) == 0:
            return []
        else:
            repos = repos[0]
        ret = repos.getElementsByTagName('item')
        return ret
    

    def open_ru_get_micex_commission(self, deals, repo_deals):
        dealcom = sum([float(d.getAttribute('broker_comm')) + float(d.getAttribute('stock_comm')) for 
                d in deals])
        repocomm = sum([float(d.getAttribute('broker_comm')) for 
                d in repo_deals])
        summcomm = dealcom + repocomm
        return summcomm

    def test_open_ru_stock_commission(self, ):
        """\brief test commission ballance for open.ru reports
        """
        if self.report_type == 'open.ru' and self.open_ru_report_type == 'stock':
            (mid, aid) = self.make_money_and_account() #@UnusedVariable
            self.load_data_into_account(aid)
            deals = self.get_deals() 
            repo_deals = self.get_repo_deals()
            summcomm = self.open_ru_get_micex_commission(deals, repo_deals)
            self.assertAlmostEqual(summcomm, 
                                   self.model._sqlite_connection.execute('select sum(commission) from deals').fetchone()[0])
            print('test stock commission passed')

    def test_open_ru_ballance(self, ):
        """\brief check if ballance for deals matches for report and database
        """
        if self.report_type == 'open.ru':
            (mid, aid) = self.make_money_and_account() #@UnusedVariable
            self.load_data_into_account(aid)
            deals = self.get_deals()
            repo_deals = self.get_repo_deals()
            
            if self.open_ru_report_type == 'stock':
                comm = self.open_ru_get_micex_commission(deals, repo_deals)
            elif self.open_ru_report_type == 'future':
                atl = self.get_account_totally_line()
                comm = self.open_ru_get_forts_comm(atl)
            ballance = sum([float(d.getAttribute('deal_sign')) *
                            float(d.getAttribute('price')) *
                            float(d.getAttribute('quantity'))
                            for d in deals])
            ballance += sum([float(d.getAttribute('deal_sign')) *
                             float(d.getAttribute('deal_price')) *
                             float(d.getAttribute('quantity'))
                             for d in repo_deals])
            ballance += 10000 - comm # 10000 is the initial account amount
            accs = self.model.list_view_accounts().fetchall()
            self.assertEqual(1, len(accs))
            self.assertAlmostEqual(ballance, accs[0]['current_money'])

    def test_open_ru_ballance_after_make_position(self, ):
        """\brief test if make position does not change the ballance of account
        """
        (mid, aid) = self.make_money_and_account() #@UnusedVariable
        self.load_data_into_account(aid)
        accs = self.model.list_view_accounts().fetchall()
        self.assertEqual(1, len(accs))
        before = accs[0]['current_money']
        self.model.tamake_positions_for_whole_account(aid)
        accs = self.model.list_view_accounts().fetchall()
        after = accs[0]['current_money']
        self.assertAlmostEqual(before, after)
    
class import_open_ru_report(import_report):

    def load_data_into_account(self, account_id):
        source = open_ru_source(self.filename, account_id, True, True)
        loader = open_ru_loader()
        loader.load(self.model, source)

class import_report1(import_open_ru_report):
    """\brief class to open 'test_report1.xml'
    """
    def __init__(self, *args, **kargs):    
        super(import_report1, self).__init__(*args, **kargs)    
        self.filename = 'tests/test_report1.xml'
        self.report_type = 'open.ru'
        self.open_ru_report_type = 'stock'
        self.deals_count = 5
        self.positions_count = 2
    
class import_report2(import_open_ru_report):
    """\brief class to open 'test_report2.xml'
    """
    def __init__(self, *args, **kargs):
        super(import_report2, self).__init__(*args, **kargs)
        self.filename = 'tests/test_report2.xml'
        self.report_type = 'open.ru'
        self.open_ru_report_type = 'stock'
        self.deals_count = 8
        self.positions_count = 4
        
class import_report3(import_open_ru_report):
    """\brief class to open 'test_report3.xml'
    """
    def __init__(self, *args, **kargs):
        super(import_report3, self).__init__(*args, **kargs)
        self.filename = 'tests/test_report3.xml'
        self.report_type = 'open.ru'
        self.open_ru_report_type = 'future'
        self.deals_count = 19
        
class import_report4(import_open_ru_report):
    """\brief class to open 'test_report4.xml'
    """
    def __init__(self, *args, **kargs):
        super(import_report4, self).__init__(*args, **kargs)
        self.filename = 'tests/test_report4.xml'
        self.report_type = 'open.ru'
        self.open_ru_report_type = 'stock'
        self.deals_count = 18

if __name__ == "__main__":
    for test_case in [import_report1,
                      import_report2,
                      import_report3,
                      import_report4]:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
