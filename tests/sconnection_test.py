#!/bin/env python
# -*- coding: utf-8 -*-
## sconnection_test ##

import random
import unittest
import sconnection
from common_methods import *
from datetime import *


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

    def test_datetime(self, ):
        """
        """
        dt = datetime(2010, 10, 11, 23, 8, 34)
        d = date(2010, 4, 2)
        t = time(12, 34, 23)
        self.conn.execute("create table dd(id, dt datetime, d date, t time)")
        self.conn.execute("insert into dd(id, dt, d, t) values (?, ?, ?, ?)", [10, dt, d, t])
        self.assertEqual((dt, d, t), self.conn.execute("select dt, d, t from dd where id = 10").fetchone())
        d2 = datetime(2011, 10, 11, 3, 4, 2)
        d3 = dt - timedelta(1)
        self.conn.executemany("insert into dd(dt) values (?)", [(d2,), (d3,)])
        self.assertEqual([(d3,), (dt,), (d2,)], self.conn.execute("select dt from dd order by dt").fetchall())
        dd2 = date(2010, 4, 4)
        dd3 = date(2009, 10, 2)
        self.conn.executemany("insert into dd(d) values (?)", [(dd2,), (dd3,)])
        self.assertEqual([(dd3,), (d,), (dd2,)], self.conn.execute("select d from dd where d is not null order by d").fetchall())
        t2 = time(12, 40, 2)
        t3 = time(2, 34, 23)
        self.conn.executemany("insert into dd(id, t) values (?, ?)",[(100, t2,), (200, t3,)])
        self.assertEqual([(t3,), (t,), (t2,)], self.conn.execute("select t from dd where t is not null order by t").fetchall())
        self.assertEqual(10 * 3600, self.conn.execute("select t1.t - t2.t from dd t1, dd t2 where t1.id = 10 and t2.id = 200").fetchone()[0])

    def test_string_reduce(self, ):
        """test reduce class and function formatting user arguments
        """
        self.conn.execute("insert into aa(id, val) values (?, ?)", ["arg1", 100])
        self.assertEqual("arg1 = 100", self.conn.execute("select argument_value(id, val) from aa where val = 100").fetchone()[0])
        self.conn.execute("insert into aa(id, val) values (?, ?)", ["arg2", 200])
        self.assertEqual("arg1 = 100, arg2 = 200", self.conn.execute("select string_reduce(x) from (select argument_value(id, val) as x from aa order by val)").fetchone()[0])

    def test_fetchone_fetchall(self, ):
        """\brief test fetchone and fetchall methods
        """
        self.conn.execute("insert into aa(id, val) values (?, ?)", [1, "one"])
        a = self.conn.execute_select("select * from aa where id = ?", [1]).fetchone()
        b = self.conn.execute_select("select * from aa where id = ?", [2]).fetchone()
        self.assertEqual(a, {"id" : 1, "val" : "one"})
        self.assertEqual(b, None)
        c = self.conn.execute_select("select * from aa where id = ?", [1]).fetchall()
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0], a)



if __name__ == '__main__':
    unittest.main()
