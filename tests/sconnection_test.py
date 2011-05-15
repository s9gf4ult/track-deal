#!/bin/env python
# -*- coding: utf-8 -*-
## sconnection_test ##

import random
import unittest
import sconnection


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
        pass

            
            
            
        


if __name__ == '__main__':
    unittest.main()
