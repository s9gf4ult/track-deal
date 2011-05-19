#!/bin/env python
# -*- coding: utf-8 -*-
## sconnection_test ##

import random
import unittest
import sconnection
from common_methods import *


class sconnection_test(unittest.TestCase):
    """tests `sconnection` methods
    Attributes:
    
    """
    ##############
    # Attributes #
    ##############
    
    
    ###########
    # Methods #
    ###########
    
    def setUp(self, ):
        """
        """
        self.conn = sconnection.sconnection(":memory:")
        self.conn.execute("create table aa(id, val)")

    def test_insert(self, ):
        """tests insert method
        """
        for c in xrange(0, 100):
            self.conn.insert("aa", {"id" : c, "val" : 10})
            
        ins = []
        for c in xrange(100, 200):
            ins.append({"id" : c, "val" : 20})
        self.conn.insert("aa", ins)
        self.assertAlmostEqual(self.conn.execute("select count(*) from aa").fetchone()[0], 200)
        self.assertAlmostEqual(self.conn.execute("select count(*) from aa where val = 20").fetchone()[0], 100)
        self.assertAlmostEqual(self.conn.execute("select sum(val) from aa").fetchone()[0], 100 * 10 + 100 * 20)

    def test_select(self, ):
        """test of execute_select method
        """
        self.conn.executemany("insert into aa(id, val) values (?, ?)", map(lambda a, b: (a, b), xrange(0, 100), xrange(200, 300)))
        self.assertEqual(99, self.conn.execute_select("select max(id) as max from aa").fetchall()[0]["max"])
        self.assertEqual(299, self.conn.execute_select("select max(val) as max from aa").fetchall()[0]["max"])
        self.assertEqual(100, len(self.conn.execute_select("select * from aa").fetchall()))
        self.assertEqual(100, self.conn.execute_select("select count(*) as count from aa").fetchall()[0]["count"])

    def test_udate(self, ):
        """tests update method
        """
        self.conn.executemany("insert into aa (id, val) values (?, ?)", map(lambda a, b: (a, b), xrange(200, 300), xrange(300, 400)))
        self.conn.update("aa", {"val" : 0}, "id > ?", [200])
        self.assertEqual(300, self.conn.execute("select sum(val) as sum from aa").fetchone()[0])
        self.conn.update("aa", {"val" : 0})
        self.conn.update("aa", {"val": 1}, "id >= ?", [250])
        self.assertEqual(50, self.conn.execute("select count(id) as count from aa where val <> 1").fetchone()[0])

    def test_commit_and_rollback(self, ):
        """
        """
        self.conn.begin_transaction()
        self.conn.executemany("insert into aa(id, val) values (?, ?)", map(lambda a, b: (a, b), xrange(0, 100), xrange(0, 100)))
        self.assertEqual(100, self.conn.execute("select count(*) from aa").fetchone()[0])
        self.conn.rollback()
        self.assertEqual(0, self.conn.execute("select count(*) from aa").fetchone()[0])
        
        self.conn.begin_transaction()
        self.conn.executemany("insert into aa(id, val) values (?, ?)", map(lambda a, b: (a, b), xrange(0, 100), xrange(0, 100)))
        self.assertEqual(100, self.conn.execute("select count(*) from aa").fetchone()[0])
        self.conn.commit()
        self.assertEqual(100, self.conn.execute("select count(*) from aa").fetchone()[0])

    def test_execute_select_cond(self, ):
        """
        """
        self.conn.executemany("insert into aa(id, val) values (?, ?)", map(lambda a, b: (a, b), xrange(100, 200), xrange(200, 300)))
        x = self.conn.execute_select_cond("aa")
        self.assertEqual(100, len(x.fetchall()))
        x = self.conn.execute_select_cond("aa", wheres = [(">=", ["id"], 150)], order_by = ["val"])
        self.assertEqual(50, len(x.fetchall()))
        a = x.fetchall()[0]["id"]
        self.assertEqual(150, a)
        x = self.conn.execute_select_cond("aa", [("id", "ident"), ("val * 2", "value")], [("<", ["id"], 120), (">", ["val"], 200)], ["id desc"])
        a = gethash(x.fetchall()[0], "ident")
        b = gethash(x.fetchall()[0], "value")
        self.assertEqual(119, a)
        self.assertNotEqual(None, b)





if __name__ == '__main__':
    unittest.main()
