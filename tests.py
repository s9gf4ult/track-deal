#! /bin/env python
# -*- coding: utf-8 -*-

import unittest
import main
import random

class balance(unittest.TestCase):
    def setUp(self):
        coats = main.xml_parser('test_report1.xml')
        coats.check_file()
        self.base = main.deals_proc(coats)
        self.accute = 4

    def test_balanced(self):
        try:
            self.base.check_balance()
        except:
            self.assertTrue(False, u'Сбалансированный отчет воспринимается как не сбалансированный')
        else:
            self.assertTrue(True)

    def test_unbalanced(self):
        self.base.connection.execute("delete from deals where id = ?",(self.base.connection.execute("select id from deals").fetchone()[0],))
        self.assertRaises(Exception, self.base.check_balance)

    def test_split_deals_balance(self):
        before = self.base.connection.execute("select sum(quantity) from deals").fetchone()[0]
        
        def split_them_all(self):
            (did, dqu) = self.base.connection.execute("select id, quantity from deals where not_actual is null and quantity > 1").fetchone() or (None, None)
            if did:
                self.base.split_deal(did, random.choice(range(1, dqu)))
                return True
            return False

        while split_them_all(self):
            pass

        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity > 1 and not_actual is null").fetchone()[0])
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity = 1 and not_actual is not null").fetchone()[0])
        self.assertNotEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where not_actual is not null").fetchone())
        if self.base.connection.execute("select count(*) from deals where not_actual is not null").fetchone()[0] > 0:
            self.assertRaises(Exception, self.base.split_deal, self.base.connection.execute("select id from deals where not_actual is not null").fetchone()[0], 1)
        (mmx,) = self.base.connection.execute("select max(quantity) from deals where not_actual is null").fetchone()
        self.assertRaises(Exception, self.base.split_deal, self.base.connection.execute("select id from deals where not_actual is null").fetchone()[0], mmx + 1)
        
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
        for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
            self.base.make_groups(ticket)
        self.assertEqual(self.accute, self.base.connection.execute("select count(*) from deal_groups").fetchone()[0]) # отчет сгенерирован так специально
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where group_id is null").fetchone()[0])
        
        for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
            (bquan,) = self.base.connection.execute("select sum(d.quantity) from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and g.ticket = ? and g.deal_sign = -1", (ticket,)).fetchone()
            (squan,) = self.base.connection.execute("select sum(d.quantity) from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null and g.ticket = ? and g.deal_sign = 1", (ticket,)).fetchone()
            self.assertEqual(bquan, squan)

        for (gid, ) in self.base.connection.execute("select id from deal_groups"):
            self.assertEqual(1, self.base.connection.execute("select count(*) from (select distinct security_name from deals where group_id = ?)", (gid,)).fetchone()[0])
            self.assertEqual(1, self.base.connection.execute("select count(*) from (select distinct deal_sign from deals where group_id = ?)", (gid,)).fetchone()[0])
            self.assertEqual(self.base.connection.execute("select deal_sign from deals where group_id = ?", (gid,)).fetchone()[0], self.base.connection.execute("select deal_sign from deal_groups where id = ?", (gid,)).fetchone()[0])
            self.assertEqual(self.base.connection.execute("select security_name from deals where group_id = ?", (gid,)).fetchone()[0], self.base.connection.execute("select ticket from deal_groups where id = ?", (gid,)).fetchone()[0])
            
    def test_split_deal_group(self):
        for (ticket,) in self.base.connection.execute("select distinct security_name from deals"):
            self.base.make_groups(ticket)

        for (gid, quant) in self.base.connection.execute("select * from (select g.id as id, sum(d.quantity) as quantity from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null group by g.id) where quantity > 1"):
            self.assertEqual(quant, self.base.connection.execute("select sum(quantity) from deals where ({0}) and not_actual is null".format(reduce(lambda a, b: u'{0} or {1}'.format(a,b), map(lambda a: u'group_id = {0}'.format(a), self.base.split_deal_group(gid, random.choice(range(1, quant))))))).fetchone()[0])

        def split_them_all(self):
            (gid, gquant) = self.base.connection.execute("select * from (select g.id as id , sum(d.quantity) as quantity from deals d inner join deal_groups g on d.group_id = g.id where d.not_actual is null group by g.id) where quantity > 1").fetchone() or (None, None)
            if gid:
                self.base.split_deal_group(gid, random.choice(range(1, gquant)))
                return True
            return False

        while split_them_all(self):
            pass

        self.assertEqual(self.base.connection.execute("select sum(quantity) from deals where not_actual is null").fetchone()[0], self.base.connection.execute("select count(*) from deal_groups").fetchone()[0])
        self.assertEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where not_actual is null").fetchone())

    def test_make_positions(self):
        self.base.make_positions()
        self.assertAlmostEqual(self.base.connection.execute("select sum(deal_sign * volume) from deals where not_actual is null and position_id is not null").fetchone()[0], self.base.connection.execute("select sum(direction * (open_volume - close_volume)) from positions").fetchone()[0])

    def test_pl_net_value(self):
        self.base.make_positions()
        (sm,) = self.base.connection.execute("select sum((deal_sign * volume) - broker_comm - stock_comm) from deals where not_actual is null and position_id is not null").fetchone()
        (spm,) = self.base.connection.execute("select sum(pl_net) from positions").fetchone()
        self.assertAlmostEqual(sm, spm)

    def test_volumes(self):
        self.base.make_positions()
        (osv, csv) = self.base.connection.execute("select sum(open_volume), sum(close_volume) from positions").fetchone()
        (oov, cov) = self.base.connection.execute("select sum(open_coast * count), sum(close_coast * count) from positions").fetchone()
        self.assertAlmostEqual(osv, oov)
        self.assertAlmostEqual(csv, cov)

class balance2(balance):
    def setUp(self):
        coats = main.xml_parser('test_report2.xml')
        coats.check_file()
        self.base = main.deals_proc(coats)
        self.accute = 8

class balance3(balance):
    def setUp(self):
        coats = main.xml_parser('test_report3.xml')
        coats.check_file()
        self.base = main.deals_proc(coats)
        self.accute = 10

class balance4(balance):
    def setUp(self):
        coats = main.xml_parser('test_report4.xml')
        coats.check_file()
        self.base = main.deals_proc(coats)
        self.accute = 12

        
if __name__ == "__main__":
    for utest in [balance, balance2, balance3, balance4]:
        suite = unittest.TestLoader().loadTestsFromTestCase(utest)
        unittest.TextTestRunner(verbosity=4).run(suite)
