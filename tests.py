#! /bin/env python
# -*- coding: utf-8 -*-

import unittest
import deals_core
import sources
import random

class balance(unittest.TestCase):
    def setUp(self):
        self.pre_setup()
        self.coats.check_file()
        self.base = deals_core.deals_proc()
        self.base.create_new(':memory:')
        self.ac1 = self.base.make_account("first_account", 100500, "RUB")
        self.ac2 = self.base.make_account("second_account", 9000, "RUB")
        self.base.get_from_source_in_account(self.ac1, self.coats)
        self.base.get_from_source_in_account(self.ac2, self.coats)

    def pre_setup(self):
        self.coats = sources.xml_parser('tests/test_report1.xml')
        self.accute = 4

    def test_check_splitted_comm(self):
        """test if commissions in report and commissions in loaded database is equal"""
        if self.coats.report.attributes['board_list'].value.find('FORTS') >= 0:
            broker_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Вознаграждение Брокера', self.coats.total_account)[0].attributes['total_value'].value))
            stock_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Биржевой сбор', self.coats.total_account)[0].attributes['total_value'].value))
            for ac in [self.ac1, self.ac2]:
                self.assertAlmostEqual(broker_comm, self.base.connection.execute("select sum(broker_comm) from deals where account_id = ?", (ac, )).fetchone()[0])
                self.assertAlmostEqual(stock_comm, self.base.connection.execute("select sum(stock_comm) from deals where account_id = ?", (ac, )).fetchone()[0])

    def test_balanced(self):
        """test if check_balance going on without errors, as expected"""
        try:
            self.base.check_balance()
        except:
            self.assertTrue(False, u'Сбалансированный отчет воспринимается как не сбалансированный')
        else:
            self.assertTrue(True)

    def test_unbalanced(self):
        """test if check_balance faults on unbalanced deals"""
        self.base.connection.execute("delete from deals where id = ?",(self.base.connection.execute("select id from deals").fetchone()[0],))
        self.assertRaises(Exception, self.base.check_balance)

    def test_split_deals_balance(self):
        """degradation tests for deals spliting"""
        before = self.base.connection.execute("select sum(quantity) from deals").fetchone()[0]
        before_vol = self.base.connection.execute("select sum(volume) from deals").fetchone()[0]
        
        def split_them_all(self):
            (did, dqu) = self.base.connection.execute("select id, quantity from deals where not_actual is null and quantity > 1").fetchone() or (None, None)
            if did:
                self.base.split_deal(did, random.choice(range(1, dqu)))
                return True
            return False

        while split_them_all(self):
            pass

        self.assertAlmostEqual(self.base.connection.execute("select sum(volume) from deals where not_actual is null").fetchone()[0], before_vol) # volume before totoal split is equal to sum of volumes of all splited deals
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity > 1 and not_actual is null").fetchone()[0]) # there is no deals unsplited
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity = 1 and not_actual is not null").fetchone()[0]) # there is no deals with quantity 1 and not actual
        self.assertNotEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where not_actual is not null").fetchone())
        if self.base.connection.execute("select count(*) from deals where not_actual is not null").fetchone()[0] > 0:
            self.assertRaises(Exception, self.base.split_deal, self.base.connection.execute("select id from deals where not_actual is not null").fetchone()[0], 1)
        (mmx,) = self.base.connection.execute("select max(quantity) from deals where not_actual is null").fetchone()
        self.assertRaises(Exception, self.base.split_deal, self.base.connection.execute("select id from deals where not_actual is null").fetchone()[0], mmx + 1)

        self.base.connection.execute("update deals set parent_deal_id = null  where parent_deal_id is not null")
        self.base.connection.execute("delete from deals where not_actual is not null")

        try:
            self.base.check_balance()
        except:
            self.assertTrue(False, u'После разбиения сделок сделки стали не сбалансированные')
        else:
            self.assertTrue(True)

        self.assertNotEqual(0, self.base.connection.execute("select count(*) from deals").fetchone()[0], u'После разбиения сделок осталось 0 сделок')
        self.assertEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals").fetchone())
        self.assertEqual(self.base.connection.execute("select sum(quantity) from deals").fetchone()[0], self.base.connection.execute("select count(*) from deals").fetchone()[0])
        self.assertEqual(before, self.base.connection.execute("select sum(quantity) from deals").fetchone()[0]) # баланс сделок до и после разбиения

    def test_make_groups(self):
        """checking correctness of making groups"""
        for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
            self.base.make_groups(ticket)
        self.assertEqual(self.accute * 2, self.base.connection.execute("select count(*) from deal_groups").fetchone()[0]) # отчет сгенерирован так специально
        for ac in [self.ac1, self.ac2]:
            self.assertEqual(self.accute, self.base.connection.execute("select count(*) from (select distinct g.id from deal_groups g inner join deals d on d.group_id = g.id where d.account_id = ?)",(ac, )).fetchone()[0])
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where group_id is null").fetchone()[0]) # all deals must be grouped
        for ac in [self.ac1, self.ac2]:
            for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
                (bquan,) = self.base.connection.execute("select sum(d.quantity) from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and g.ticket = ? and g.deal_sign = -1 and d.account_id = ?", (ticket, ac)).fetchone()
                (squan,) = self.base.connection.execute("select sum(d.quantity) from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and g.ticket = ? and g.deal_sign = 1 and d.account_id = ?", (ticket, ac)).fetchone()
                self.assertEqual(bquan, squan)

        for (gid, ) in self.base.connection.execute("select id from deal_groups"):
            self.assertEqual(1, self.base.connection.execute("select count(*) from (select distinct security_name from deals where group_id = ?)", (gid,)).fetchone()[0]) # each group must have deals just for one ticket assigned to
            self.assertEqual(1, self.base.connection.execute("select count(*) from (select distinct deal_sign from deals where group_id = ?)", (gid,)).fetchone()[0]) # all deals assigned to group must be in one sign
            self.assertEqual(1, self.base.connection.execute("select count(*) from (select distinct account_id from deals where group_id = ?)", (gid,)).fetchone()[0]) # all delas assigned to group must be assigned to one account
            self.assertEqual(self.base.connection.execute("select deal_sign from deals where group_id = ?", (gid,)).fetchone()[0], self.base.connection.execute("select deal_sign from deal_groups where id = ?", (gid,)).fetchone()[0]) # sign of deals must be equal to sign of group
            self.assertEqual(self.base.connection.execute("select security_name from deals where group_id = ?", (gid,)).fetchone()[0], self.base.connection.execute("select ticket from deal_groups where id = ?", (gid,)).fetchone()[0]) # ticket of group must be equal to ticket of deals
            
    def test_split_deal_group(self):
        """degradation tests of splitting deal groups"""
        for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
            self.base.make_groups(ticket)

        for (gid, quant) in self.base.connection.execute("select * from (select g.id as id, sum(d.quantity) as quantity from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null group by g.id) where quantity > 1"):
            self.assertEqual(quant, self.base.connection.execute("select sum(quantity) from deals where ({0}) and not_actual is null".format(reduce(lambda a, b: u'{0} or {1}'.format(a,b), map(lambda a: u'group_id = {0}'.format(a), self.base.split_deal_group(gid, random.choice(range(1, quant))))))).fetchone()[0]) # quantity of splited groups is equal to quantity of original group

        def split_them_all(self):
            (gid, gquant) = self.base.connection.execute("select * from (select g.id as id , sum(d.quantity) as quantity from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null group by g.id) where quantity > 1").fetchone() or (None, None)
            if gid:
                self.base.split_deal_group(gid, random.choice(range(1, gquant)))
                return True
            return False

        while split_them_all(self):
            pass

        self.assertEqual(self.base.connection.execute("select sum(quantity) from deals where not_actual is null").fetchone()[0], self.base.connection.execute("select count(*) from deal_groups").fetchone()[0]) # count of groups is equal to sum(quantiry) of all deals assigned to
        self.assertEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where not_actual is null").fetchone())

    def test_make_positions(self):
        """test of positions volumes"""
        self.base.make_positions()
        self.assertAlmostEqual(self.base.connection.execute("select sum(deal_sign * volume) from deals where not_actual is null and position_id is not null").fetchone()[0], self.base.connection.execute("select sum(direction * (open_volume - close_volume)) from positions").fetchone()[0]) # balance of deals and positions volumes
        self.assertAlmostEqual(self.base.connection.execute("select sum(broker_comm + stock_comm) from deals where not_actual is null and position_id is not null").fetchone()[0],
                               self.base.connection.execute("select sum(broker_comm + stock_comm) from positions").fetchone()[0])

    def test_positions_view(self):
        self.base.make_positions()
        for (acc_id, ) in self.base.connection.execute("select distinct id from accounts"):
            self.base.recalculate_position_attributes(acc_id)
            self.assertAlmostEqual(self.base.connection.execute("select last_money from accounts_view where id = ? limit 1", (acc_id,)).fetchone()[0],
                                   self.base.connection.execute("select net_after from positions_view where account_id = ? order by close_datetime desc, open_datetime desc limit 1", (acc_id, )).fetchone()[0])
            self.assertAlmostEqual(self.base.connection.execute("select sum(d.stock_comm + d.broker_comm) from deals d where d.account_id = ? and d.not_actual is null", (acc_id,)).fetchone()[0],
                                   self.base.connection.execute("select comm_after from positions_view where account_id = ? order by close_datetime desc, open_datetime desc limit 1", (acc_id,)).fetchone()[0])
            (net, gross, comm) = self.base.connection.execute("select net_after, gross_after, comm_after from positions_view where account_id = ? order by close_datetime desc, open_datetime desc limit 1", (acc_id,)).fetchone()
            self.assertAlmostEqual(net, gross - comm)

    def test_pl_net_value(self):
        """testing of pl_net correctness"""
        self.base.make_positions()
        (sm,) = self.base.connection.execute("select sum((deal_sign * volume) - broker_comm - stock_comm) from deals where not_actual is null and position_id is not null").fetchone()
        (spm,) = self.base.connection.execute("select sum(pl_net) from positions").fetchone()
        self.assertAlmostEqual(sm, spm) # balance between pl_net and volume differences in positions

    def test_volumes(self):
        """checking volumes of deals and positions"""
        self.base.make_positions()
        for (vol, price ,quant, ticket) in self.base.connection.execute("select volume, price, quantity, security_name from deals where not_actual is null and position_id is not null"):
            self.assertAlmostEqual(float(vol), float(price * quant), 5, u'{0}::: vol={1}, price={2}, quantity={3}'.format(ticket, vol, price, quant)) # checking deals volumes correctness
        (osv, csv) = self.base.connection.execute("select sum(open_volume), sum(close_volume) from positions").fetchone()
        (oov, cov) = self.base.connection.execute("select sum(open_coast * count), sum(close_coast * count) from positions").fetchone()
        self.assertAlmostEqual(osv, oov) # checking of positions correctness 
        self.assertAlmostEqual(csv, cov)

class balance2(balance):
    def pre_setup(self):
        self.coats = sources.xml_parser('tests/test_report2.xml')
        self.accute = 8

class balance3(balance):
    def pre_setup(self):
        self.coats = sources.xml_parser('tests/test_report3.xml')
        self.accute = 10

class balance4(balance):
    def pre_setup(self):
        self.coats = sources.xml_parser('tests/test_report4.xml')
        self.accute = 14

class sources_xml_parser(unittest.TestCase):
    def setUp(self):
        self.s = self.open_file()
        self.ss = self.open_file()
        self.s.check_file()
        self.ss.check_file()

    def open_file(self):
        return sources.xml_parser('tests/test_report1.xml')

    def test_check_sha1(self):
        """open.ru report parser gets equal sha1 every time"""
        d = self.s.get_deals_list()
        dd = self.ss.get_deals_list()
        self.assertEqual(len(d), len(dd))
        for (c, cc) in map(lambda a, b: (a, b), d, dd):
            self.assertEqual(c, cc)

class sources_xml_parser2(sources_xml_parser):
    def open_file(self):
        return sources.xml_parser('tests/test_report2.xml')
    
class sources_xml_parser3(sources_xml_parser):
    def open_file(self):
        return sources.xml_parser('tests/test_report3.xml')
        
class sources_xml_parser4(sources_xml_parser):
    def open_file(self):
        return sources.xml_parser('tests/test_report4.xml')
    
if __name__ == "__main__":
    for utest in [balance, balance2, balance3, balance4, sources_xml_parser,
                  sources_xml_parser2, sources_xml_parser3, sources_xml_parser4]:
        suite = unittest.TestLoader().loadTestsFromTestCase(utest)
        unittest.TextTestRunner(verbosity=4).run(suite)
