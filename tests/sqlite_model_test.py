import sqlite_model
import unittest
import sqlite3
import random
import os
from common_methods import *

class sqlite_model_test(unittest.TestCase):
    """
    tests sqlite model class
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
        self.model = sqlite_model.sqlite_model()
        self.model.connect(":memory:")

    def test_dbinit(self, ):
        """tests dbinit execution
        """
        self.model.dbinit()
        self.assertEqual(1, self.model._sqlite_connection.execute_select("select count(name) as count from sqlite_master where name = ? and type = 'table'", ('deals', )).fetchall()[0]["count"])
        self.assertEqual(20, self.model._sqlite_connection.execute_select("select count(*) as count from sqlite_master where type = 'table'").fetchall()[0]["count"])

    def test_dbtemp(self, ):
        """tests dbtemp execution
        """
        self.assertRaises(sqlite3.OperationalError, self.model.dbtemp)
        self.model = sqlite_model.sqlite_model()
        self.model.connect(":memory:")
        self.model.dbinit()
        self.model.dbtemp()
        self.assertEqual(9, self.model._sqlite_connection.execute_select("select count(*) as count from sqlite_temp_master where type = 'table'").fetchall()[0]["count"])

    def test_create_new_and_open(self, ):
        """tests of creation new database and opening existing
        """
        fname = './tmpfile.sqlite'
        try:
            os.remove(fname)
        except:
            print('already removed')
        md = sqlite_model.sqlite_model()
        md.create_new(fname)
        md.disconnect()
        del md
        mx = sqlite_model.sqlite_model()
        mx.open_existing(fname)
        mx.disconnect()
        del mx
        os.remove(fname)

    def test_decorators(self, ):
        """Tests how good decorators work
        """
        self.model.disconnect()
        self.assertRaises(Exception, self.model.begin_transaction)
        self.assertRaises(Exception, self.model.disconnect)

    def test_global_parameters(self, ):
        """tests actions on global parameters
        """
        self.model.dbinit()
        self.model.dbtemp()
        self.model.add_global_data({"p1" : 100, "p2" : 200})
        self.assertEqual(100, self.model.get_global_data("p1"))
        self.model.add_global_data({"p1" : 300})
        self.assertEqual(300, self.model.get_global_data("p1"))
        self.assertEqual(200, self.model.get_global_data("p2"))
        self.assertSetEqual(set(["p1", "p2"]), set(self.model.list_global_data()))
        self.model.remove_global_data("p1")
        self.assertEqual(None, self.model.get_global_data("p1"))
        self.model.remove_global_data(["p2"])
        self.assertEqual(None, self.model.get_global_data("p2"))
        self.assertSetEqual(set([]), set(self.model.list_global_data()))

    def test_database_attributes(self, ):
        """tests actions on global parameters
        """
        self.model.dbinit()
        self.model.dbtemp()
        self.model.add_database_attributes({"p1" : 100, "p2" : 200})
        self.assertEqual(100, self.model.get_database_attribute("p1"))
        self.model.add_database_attributes({"p1" : 300})
        self.assertEqual(300, self.model.get_database_attribute("p1"))
        self.assertEqual(200, self.model.get_database_attribute("p2"))
        self.assertSetEqual(set(["p1", "p2"]), set(self.model.list_database_attributes()))
        self.model.remove_database_attribute("p1")
        self.assertEqual(None, self.model.get_database_attribute("p1"))
        self.model.remove_database_attribute(["p2"])
        self.assertEqual(None, self.model.get_database_attribute("p2"))
        self.assertSetEqual(set([]), set(self.model.list_database_attributes()))

    def test_papers(self, ):
        """tests method for make and get papers
        """
        self.model.dbinit()
        self.model.dbtemp()
        paid = self.model.create_paper(type = "stock", name = "something", class_name = "paperclass")
        pp = self.model.get_paper(paid)
        pid = pp["id"]
        self.assertTrue(pp.has_key("id"))
        self.assertIsInstance(pp["id"], int)
        for k in pp.keys():
            if k == "id":
                del pp[k]
            if pp.has_key(k) and pp[k] == None:
                del pp[k]
        self.assertDictEqual({"type" : "stock", "name" : "something", "class" : "paperclass"}, pp)
        self.assertEqual(None, self.model.get_paper("stock", "adsfa"))
        self.assertEqual(pid, self.model.get_paper("stock", "something")["id"])
        self.model.remove_paper(pid)
        self.assertEqual(None, self.model.get_paper("stock", "something"))
        self.model.create_paper("type", "name")
        self.assertIsInstance(self.model.get_paper("type", "name"), dict)
        self.model.remove_paper("type", "name")
        self.assertEqual(None, self.model.get_paper("type", "name"))
        self.assertListEqual([], self.model.list_papers().fetchall())
        
    def test_candles(self, ):
        """tests creation and deleting candles
        """
        self.model.dbinit()
        self.model.dbtemp()
        paid = self.model.create_paper("stock", "name")
        self.model.create_candles(paid, {"duration" : "1min", "open_datetime" : 100, "close_datetime" : 200, "open_value" : 1.2, "close_value" : 2.1, "min_value" : 1.1, "max_value" : 3, "value_type" : "price", "volume" : 200})
        self.assertEqual(1, len(self.model.list_candles(paid).fetchall()))
        cndls = []
        for x in xrange(0, 100):
            cc = {"duration" : "1min", "open_datetime" : x * 60, "close_datetime" : x*60 + 59, "open_value" : 10, "close_value" : 20, "min_value" : 5, "max_value" : 22, "volume" : 0, "value_type" : "price"}
            cndls.append(cc)
        self.model.create_candles(paid, cndls)
        self.assertEqual(101, len(self.model.list_candles(paid).fetchall()))
        self.assertIsInstance(self.model.list_candles(paid).fetchall()[0], dict)
        self.model.remove_paper(paid)
        self.assertEqual(0, len(self.model.list_candles(paid).fetchall()))

    def test_moneys(self, ):
        """tests money creation and deletion
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU", "rubles")
        self.assertEqual(1, len(self.model.list_moneys(["name"]).fetchall()))
        self.model.remove_money("RU")
        self.assertEqual(0, len(self.model.list_moneys().fetchall()))
        mid = self.model.create_money("RU", "rubles")
        self.assertEqual(1, len(self.model.list_moneys(["name"]).fetchall()))
        self.model.remove_money(mid)
        self.assertEqual(0, len(self.model.list_moneys().fetchall()))

    def test_points(self, ):
        """test point
        """
        self.model.dbinit()
        self.model.dbtemp()
        

        

        

if __name__ == '__main__':
    unittest.main()
