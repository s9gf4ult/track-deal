import sqlite_model
import unittest
import sqlite3
import random
import os
from common_methods import *
from datetime import *

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
        self.assertEqual(set(["p1", "p2"]), set(self.model.list_global_data()))
        self.model.remove_global_data("p1")
        self.assertEqual(None, self.model.get_global_data("p1"))
        self.model.remove_global_data(["p2"])
        self.assertEqual(None, self.model.get_global_data("p2"))
        self.assertEqual(set([]), set(self.model.list_global_data()))

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
        self.assertEqual(set(["p1", "p2"]), set(self.model.list_database_attributes()))
        self.model.remove_database_attribute("p1")
        self.assertEqual(None, self.model.get_database_attribute("p1"))
        self.model.remove_database_attribute(["p2"])
        self.assertEqual(None, self.model.get_database_attribute("p2"))
        self.assertEqual(set([]), set(self.model.list_database_attributes()))

    def test_papers(self, ):
        """tests method for make and get papers
        """
        self.model.dbinit()
        self.model.dbtemp()
        paid = self.model.create_paper(type = "stock", name = "something", class_name = "paperclass")
        pp = self.model.get_paper(paid)
        pid = pp["id"]
        self.assertTrue(pp.has_key("id"))
        self.assertTrue(isinstance(pp["id"], int))
        for k in pp.keys():
            if k == "id":
                del pp[k]
            if pp.has_key(k) and pp[k] == None:
                del pp[k]
        self.assertEqual({"type" : "stock", "name" : "something", "class" : "paperclass"}, pp)
        self.assertEqual(None, self.model.get_paper("stock", "adsfa"))
        self.assertEqual(pid, self.model.get_paper("stock", "something")["id"])
        self.model.remove_paper(pid)
        self.assertEqual(None, self.model.get_paper("stock", "something"))
        self.model.create_paper("type", "name")
        self.assertTrue(isinstance(self.model.get_paper("type", "name"), dict))
        self.model.remove_paper("type", "name")
        self.assertEqual(None, self.model.get_paper("type", "name"))
        self.assertEqual([], self.model.list_papers().fetchall())
        
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
        self.assertTrue(isinstance(self.model.list_candles(paid).fetchall()[0], dict))
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
        mid = self.model.create_money("RU")
        paid = self.model.create_paper("type", "name")
        ppid = self.model.create_point(paid, mid, 1000, 1)
        self.assertEqual(1000, self.model.get_point(paid, mid)["point"])
        self.assertEqual(1, self.model.get_point(ppid)["step"])
        self.assertRaises(Exception, self.model.create_point, paid, mid)
        self.assertEqual(1, len(self.model.list_points(paid).fetchall()))
        self.model.remove_point(ppid)
        self.assertEqual(0, len(self.model.list_points().fetchall()))
        ppid = self.model.create_point(paid, mid, 1000, 1)
        self.model.remove_point(paid, mid)
        self.assertEqual(0, len(self.model.list_points().fetchall()))
        ppid = self.model.create_point(paid, mid, 1000, 1)
        self.model.remove_paper(paid)
        self.assertEqual(0, len(self.model.list_points().fetchall()))

    def test_account(self, ):
        """tests add and delete account
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("ac1", mid, 100)
        self.assertEqual(1, len(self.model.list_accounts(["name"]).fetchall()))
        self.model.remove_account("ac1")
        self.assertEqual(0, len(self.model.list_accounts().fetchall()))
        self.model.create_account("ac2", mid, 200, "ruru")
        self.assertEqual("ruru", self.model.list_accounts().fetchall()[0]["comments"])

    def test_deals(self, ):
        """test deals
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("name", mid, 100)
        paid = self.model.create_paper("stock", "stock1", "fjfj")
        did = self.model.create_deal(aid, {"paper_id" : paid, "count" : 10, "direction" : -1, "points" : 200, "commission" : 0.1, "datetime" : datetime(2010, 10, 10)})
        self.assertEqual(1, len(self.model.list_deals(aid).fetchall()))
        self.model.remove_deal(did)
        self.assertEqual(0, len(self.model.list_deals().fetchall()))
        did = self.model.create_deal(aid, {"paper_id" : paid, "count" : 5, "direction" : 1, "points" : 100, "commission" : 2.3, "datetime" : datetime(2010, 10, 11), "user_attributes" : {"at1" : 10, "at2" : "thecap"}, "stored_attributes" : {"at1" : 20, "at2" : 2.3}})
        ua = self.model.get_user_deal_attributes(did)
        sa = self.model.get_stored_deal_attributes(did)
        self.assertEqual({"at1" : 10, "at2" : "thecap"}, ua)
        self.assertEqual({"at1" : 20, "at2" : 2.3}, sa)

    def test_positions(self, ):
        """
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("ac1", mid, 1000)
        paid = self.model.create_paper("stock", "stock")
        di1 = self.model.create_deal(aid, {"paper_id" : paid,
                                           "count" : 10,
                                           "direction" : -1,
                                           "points" : 100,
                                           "datetime" : 100})
        di2 = self.model.create_deal(aid, {"paper_id" :paid,
                                           "count" : 10,
                                           "direction" : 1,
                                           "points" : 110,
                                           "datetime" : 150})
        gid1 = self.model.create_group(di1)
        gid2 = self.model.create_group(di2)
        pid = self.model.create_position(gid1, gid2)
        self.assertEqual(1, len(self.model.list_positions(aid).fetchall()))
        for (field, value) in [("count", 9),
                               ("direction", -1),
                               ("datetime", 99)]:
            di1 = self.model.create_deal(aid, {"paper_id" : paid,
                                               "count" : 10,
                                               "direction" : -1,
                                               "points" : 100,
                                               "datetime" : 100})
            x = {"paper_id" : paid,
                 "count" : 10,
                 "direction" : 1,
                 "points" : 110,
                 "datetime" : 110}
            x[field] = value
            di2 = self.model.create_deal(aid, x)
            gid1 = self.model.create_group([di1])
            gid2 = self.model.create_group(di2)
            self.assertRaises(Exception, self.model.create_position, gid1, gid2)
            
    def test_calculate_deals(self, ):
        """complex test of deal_view recalculation and group calculations
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("ac1", "RU", 1000)
        paid = self.model.create_paper("stock", "stock")
        dd = datetime.now()
        x = 1000
        ll = [(100, 1, 120, 1.2, 10),
              (111, 1.11, 100, 1, 10),
              (80, 0.8, 100, 1, 5)]
        for (oprice, ocomm, cprice, ccomm, count) in ll:
            self.model.create_deal(aid, {"paper_id" : paid,
                                         "direction" : -1,
                                         "count" : count,
                                         "points" : oprice,
                                         "commission" : ocomm,
                                         "datetime" : dd})
            dd += timedelta(1)
            self.model.create_deal(aid, {"paper_id" : paid,
                                         "direction" : 1,
                                         "count" : count,
                                         "points" : cprice,
                                         "commission" : ccomm,
                                         "datetime" : dd})
            dd += timedelta(1)
            x += ((cprice - oprice) * count) - ocomm - ccomm
        self.model.calculate_deals(aid, paid)
        self.assertEqual(2 * len(ll), self.model._sqlite_connection.execute("select count(dw.id) from deals_view dw inner join deals d on dw.deal_id = d.id where d.account_id = ? and d.paper_id = ?", [aid, paid]).fetchone()[0])
        self.assertAlmostEqual(x, self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? and paper_id = ? order by datetime desc limit 1", [aid, paid]).fetchone()[0])
        self.assertEqual((ll[-1][-1], 0), self.model._sqlite_connection.execute("select paper_ballance_before, paper_ballance_after from deals_view where account_id = ? and paper_id = ? order by datetime desc limit 1", [aid, paid]).fetchone())
        point = 10
        self.model.create_point(paid, mid, point, 0.001)
        self.model.recalculate_deals(aid, paid)
        xx = 1000
        for (oprice, ocomm, cprice, comm, count) in ll:
            xx += ((cprice - oprice) * count * point) - ocomm - comm
        self.assertAlmostEqual(xx, self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? and paper_id = ? order by datetime desc limit 1", [aid, paid]).fetchone()[0])
        self.model.make_groups(aid, paid)
        self.assertEqual(2 * len(ll), len(self.model.list_groups(aid, paid).fetchall()))
        self.assertEqual(len(ll), self.model._sqlite_connection.execute("select count(*) from deal_groups where direction = -1").fetchone()[0])
        self.assertEqual(len(ll), self.model._sqlite_connection.execute("select count(*) from deal_groups where direction = 1").fetchone()[0])

    def test_groups(self, ):
        """special test of group making
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("ac1", mid, 1000)
        paid = self.model.create_paper("stock", "stock")
        dd = datetime(2010, 10, 10)
        for direc in [-1, -1, 1, -1]:
            for x in xrange(0, 5):
                self.model.create_deal(aid, {"paper_id" : paid,
                                             "points" : 100,
                                             "commission" : 1,
                                             "direction" : direc,
                                             "count" : 1,
                                             "datetime" : dd})
                dd += timedelta(0, 4)
            if direc == -1:
                dd += timedelta(0, 5)
        self.model.make_groups(aid, paid)
        self.assertEqual(4, self.model._sqlite_connection.execute("select count(*) from deal_groups").fetchone()[0])
            
                     


        

if __name__ == '__main__':
    unittest.main()
