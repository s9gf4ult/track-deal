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
        def split_them_all(self):
            (did, dqu) = self.base.connection.execute("select id quantity from deals where (position_id is null or position_id <> -1) and quantity > 1").fetchone() or (None, None)
            if did:
                self.base.split_deal(did, random.choise(range(1, dqu)))
                return True
            return False

        while split_them_all(self):
            pass

        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity > 1 and position_id <> -1").fetchone()[0])
        self.assertEqual(0, self.base.connection.execute("select count(*) from deals where quantity = 1 and position_id = -1").fetchone()[0])
        self.assertNotEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where position_id = -1").fetchone())
        self.base.connection.execute("delete from deals where position_id is not null")

        try:
            self.base.check_balance()
        except:
            self.assertTrue(False, u'После разбиения сделок сделки стали не сбалансированные')
        else:
            self.assertTrue(True)

        self.assertNotEqual(0, self.base.connection.execute("select count(*) from deals").fetchone()[0], u'После разбиения сделок осталось 0 сделок')
        self.assertEqual((1, 1), self.base.connection.execute("select min(quantity), max(quantity) from deals where quantity > 1").fetchone())
        self.assertEqual(self.base.connection.execute("select sum(quantity) from deals").fetchone()[0], self.base.connection.execute("select count(*) from deals").fetchone()[0])


if __name__ == "__main__":
    unittest.main()
