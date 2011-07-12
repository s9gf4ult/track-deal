import sqlite_model
import unittest
import sqlite3
import random
import os
from common_methods import *
from datetime import *
import random
from copy import copy

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
        self.assertEqual(21, self.model._sqlite_connection.execute_select("select count(*) as count from sqlite_master where type = 'table'").fetchall()[0]["count"])

    def test_dbtemp(self, ):
        """tests dbtemp execution
        """
        self.assertRaises(sqlite3.OperationalError, self.model.dbtemp)
        self.model = sqlite_model.sqlite_model()
        self.model.connect(":memory:")
        self.model.dbinit()
        self.model.dbtemp()
        self.assertEqual(10, self.model._sqlite_connection.execute_select("select count(*) as count from sqlite_temp_master where type = 'table'").fetchall()[0]["count"]) # 9 tables + 1 special (autoincrement)

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
        (mid, aid, paid) = self.deals_init()
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
        (mid, aid, paid) = self.deals_init()
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
        (mid, aid, paid) = self.deals_init()
        dd = datetime.now()
        x = 1000
        ll = [(100, 1, 120, 1.2, 10),
              (111, 1.11, 100, 1, 10),
              (80, 0.8, 100, 1, 5)]
        dds = []
        for (oprice, ocomm, cprice, ccomm, count) in ll:
            dds.append({"paper_id" : paid,
                        "direction" : -1,
                        "count" : count,
                        "points" : oprice,
                        "commission" : ocomm,
                        "datetime" : dd})
            dd += timedelta(1)
            dds.append({"paper_id" : paid,
                        "direction" : 1,
                        "count" : count,
                        "points" : cprice,
                        "commission" : ccomm,
                        "datetime" : dd})
            dd += timedelta(1)
            x += ((cprice - oprice) * count) - ocomm - ccomm
        self.model.create_deal(aid, dds)
        self.model.calculate_deals(aid)
        self.assertEqual(2 * len(ll), self.model._sqlite_connection.execute("select count(dw.id) from deals_view dw inner join deals d on dw.deal_id = d.id where d.account_id = ? and d.paper_id = ?", [aid, paid]).fetchone()[0])
        self.assertAlmostEqual(x, self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? and paper_id = ? order by datetime desc limit 1", [aid, paid]).fetchone()[0])
        self.assertEqual((ll[-1][-1], 0), self.model._sqlite_connection.execute("select paper_ballance_before, paper_ballance_after from deals_view where account_id = ? and paper_id = ? order by datetime desc limit 1", [aid, paid]).fetchone())
        point = 10
        self.model.create_point(paid, mid, point, 0.001)
        self.model.recalculate_deals(aid)
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
        (mid, aid, paid) = self.deals_init()
        dd = datetime(2010, 10, 10)
        dds = []
        for direc in [-1, -1, 1, -1]:
            for x in xrange(0, 5):
                dds.append({"paper_id" : paid,
                            "points" : 100,
                            "commission" : 1,
                            "direction" : direc,
                            "count" : 1,
                            "datetime" : dd})
                dd += timedelta(0, 4)
            if direc == -1:
                dd += timedelta(0, 5)
        self.model.create_deal(aid, dds)
        self.model.make_groups(aid, paid)
        self.assertEqual(4, self.model._sqlite_connection.execute("select count(*) from deal_groups").fetchone()[0])
        dd += timedelta(1)
        dds = []
        for x in xrange(0, 10):
            dds.append({"paper_id" : paid,
                        "points" : 200,
                        "commission" : 2,
                        "direction" : 1,
                        "count" : 3,
                        "datetime" : dd})
            dd += timedelta(0, 2)
        self.model.create_deal(aid, dds)
        self.model.make_groups(aid, paid)
        self.assertEqual(5, len(self.model.list_groups(aid, paid).fetchall()))
                     
    def deals_init(self, ):
        """
        """
        self.model.dbinit()
        self.model.dbtemp()
        mid = self.model.create_money("RU")
        aid = self.model.create_account("ac1", mid, 1000)
        paid = self.model.create_paper("stock", "stock")
        return (mid, aid, paid)

        
    def test_group_replacement(self, ):
        """test that when you create new group with deals assigned to other group, they automatically disconnect from old group
        """
        (mid, aid, paid) = self.deals_init()
        dls = []
        d = datetime(2010, 10, 10)
        for x in xrange(0, 10):
            dls.append(self.model.create_deal(aid, {"paper_id" : paid,
                                                    "datetime" : d,
                                                    "count" : 10,
                                                    "direction" : -1,
                                                    "commission" : 0.1,
                                                    "points" : 100}))
            d += timedelta(0, 3)
        self.model.make_groups(aid, paid)
        gid1 = self.model.list_groups(aid, paid).fetchall()[0]["id"]
        gid2 = self.model.create_group(dls[:5])
        self.assertEqual(set(dls[:5]), set(map(lambda a: a[0], self.model._sqlite_connection.execute("select d.id from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ?", [gid2]).fetchall())))
        self.assertEqual(set(dls[5:]), set(map(lambda a: a[0], self.model._sqlite_connection.execute("select d.id from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ?", [gid1]).fetchall())))


    def test_split_deals(self, ):
        """reduction test of splitting deals
        """
        (mid, aid, paid) = self.deals_init()
        d = datetime(2010, 10, 10)
        sumc = 0
        dds = []
        for x in xrange(0, 10):
            cc = random.randint(1, 100)
            sumc += cc
            dds.append({"paper_id" : paid,
                        "count" : cc,
                        "direction" : (random.random() > 0.5 and 1 or -1),
                        "commission" : 1,
                        "points" : random.random() * 100 + 100,
                        "datetime" : d})
            d += timedelta(0, random.randint(1, 20))
        self.model.create_deal(aid, dds)

        def go_on():
            x = self.model._sqlite_connection.execute_select("select d.* from deals d where d.count > 1 and not exists(select dd.id from deals dd where dd.parent_deal_id = d.id) limit 1").fetchall()
            if len(x) == 0:
                return False
            x = x[0]
            rnd = random.randint(1, x["count"] - 1)
            (d, dd) = self.model.split_deal(x["id"], rnd)
            self.assertEqual(rnd, self.model._sqlite_connection.execute("select count from deals where id = ?", [d]).fetchone()[0])
            self.assertEqual(x["count"] - rnd, self.model._sqlite_connection.execute("select count from deals where id = ?", [dd]).fetchone()[0])
            self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from deals_view where deal_id = ?", [x["id"]]).fetchone()[0])
            self.assertEqual(2, self.model._sqlite_connection.execute("select count(*) from deals_view where deal_id = ? or deal_id = ?", [d, dd]).fetchone()[0])
                             
            return True
        
        while go_on():
            pass

        self.assertEqual(0, self.model._sqlite_connection.execute("select count(d.id) from deals d where d.count <> 1 and not exists(select dd.id from deals dd where dd.parent_deal_id = d.id)").fetchone()[0])
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(dw.id) from deals_view dw inner join deals d on dw.deal_id = d.id where d.count <> 1 or dw.count <> 1").fetchone()[0])
        self.assertEqual(sumc, self.model._sqlite_connection.execute("select count(*) from deals_view").fetchone()[0])
        self.assertEqual(sumc, self.model._sqlite_connection.execute("select sum(d.count) as sum from deals d where not exists(select dd.id from deals dd where dd.parent_deal_id = d.id)").fetchone()[0])

    def test_split_group(self, ):
        """reduction test for split_group
        """
        (mid, aid, paid) = self.deals_init()
        d = datetime(2010, 10, 10)
        sumc = 0
        sumv = 0
        dds = []
        for x in xrange(0, 10):
            cc = random.randint(1, 10)
            dirc = (random.random() > 0.5 and -1 or 1)
            pr = random.random() * 100 + 100
            sumc += cc
            sumv += dirc * cc * pr
            dds.append({"paper_id" : paid,
                        "datetime" : d,
                        "count" : cc,
                        "points" : pr,
                        "direction" : dirc,
                        "commission" : 1})
            d += timedelta(0, random.randint(1, 7))
        self.model.create_deal(aid, dds)
        self.model.make_groups(aid, paid)
        
        def go_on():
            g = self.model._sqlite_connection.execute_select("select * from (select g.id as id, sum(d.count) as count from deal_groups g inner join deal_group_assign dg on dg.group_id = g.id inner join deals d on d.id = dg.deal_id group by g.id) where count > 1 limit 1").fetchall()
            if len(g) == 0:
                return False
            g = g[0]
            rnd = random.randint(1, g["count"] - 1)
            (g1, g2) = self.model.split_group(g["id"], rnd)
            self.assertNotEqual(None, g1)
            self.assertNotEqual(None, g2)
            self.assertEqual(1, self.model._sqlite_connection.execute("select count(*) from deal_groups where id = ?", [g1]).fetchone()[0])
            self.assertEqual(1, self.model._sqlite_connection.execute("select count(*) from deal_groups where id = ?", [g2]).fetchone()[0])
            self.assertTrue(1 <= self.model._sqlite_connection.execute("select count(d.id) from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on g.id = dg.group_id where g.id = ? group by g.id", [g1]).fetchone()[0])
            self.assertTrue(1 <= self.model._sqlite_connection.execute("select count(d.id) from deals d inner join deal_group_assign dg on dg.deal_id = d.id inner join deal_groups g on g.id = dg.group_id where g.id = ? group by g.id", [g2]).fetchone()[0])
            
            (cc1, ) = self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [g1]).fetchone()
            self.assertEqual(cc1, rnd)
            (cc2, ) = self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [g2]).fetchone()
            self.assertEqual(cc2, g["count"] - rnd)
            return True
        while go_on():
            pass
        
        self.assertEqual(sumc, self.model._sqlite_connection.execute("select count(*) from deals_view").fetchone()[0])
        self.assertAlmostEqual(sumv, self.model._sqlite_connection.execute("select sum(volume * direction) from deals_view").fetchone()[0])
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from deals_view where count <> 1").fetchone()[0])

    def test_try_make_ballanced_groups(self, ):
        """
        """
        (mid, aid, paid) = self.deals_init()
        d = datetime(2010, 10, 10)
        for (a, b) in [(1, 10),
                       (20, 12),
                       (3, 3),
                       (10, 10),
                       (1, 1)]:
            for x in [a, b]:
                self.model.create_group(self.model.create_deal(aid, {"paper_id" : paid,
                                                                     "commission" : 0.1,
                                                                     "direction" : 1,
                                                                     "points" : 100,
                                                                     "count" : x,
                                                                     "datetime" : d}))
                d += timedelta(0, random.randint(1, 10))
            (g1, g2) = self.model._sqlite_connection.execute_select("select * from deal_groups")
            self.assertNotEqual(None, g1)
            self.assertNotEqual(None, g2)
            (g1, g2) = self.model.try_make_ballanced_groups(g1["id"], g2["id"])
            self.assertEqual(self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [g1]).fetchone()[0], self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [g2]).fetchone()[0])
            self.assertEqual(min(a, b), self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deal_group_assign dg on dg.deal_id = d.id where dg.group_id = ? group by dg.group_id", [g1]).fetchone()[0])
            self.model._sqlite_connection.execute("delete from deal_groups")
        
    def test_make_positions(self, ):
        """
        """
        d = datetime(2010, 10, 10)
        (mid, aid, paid) = self.deals_init()
        dds = []
        for x in xrange(0, 10):
            count = random.randint(1, 100)
            price = random.random() * 100 + 100
            direction = (random.random() > 0.5 and 1 or -1)
            for dirr in [direction, -direction]:
                for y in xrange(0, 10):
                    dds.append({"paper_id" : paid,
                                "count" : count,
                                "commission" : 0.1,
                                "direction" : dirr,
                                "datetime" : d,
                                "points" : price})
                    d += timedelta(0, random.randint(1, 7))
        self.model.create_deal(aid, dds)
        self.model.make_positions(aid, paid)
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from deals where position_id is null").fetchone()[0])
        for p in self.model._sqlite_connection.execute_select("select * from positions"):
            self.assertAlmostEqual(0, self.model._sqlite_connection.execute("select sum(d.count * d.direction) from deals d where d.position_id = ?", [p["id"]]).fetchone()[0])
            self.assertEqual(p["count"], self.model._sqlite_connection.execute("select sum(d.count) from deals d where d.direction = 1 and d.position_id = ?", [p["id"]]).fetchone()[0])
        self.model.remake_groups(aid, paid)
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from deal_groups").fetchone()[0])
        self.model.disconnect()
        
        self.setUp()
        (mid, aid, paid) = self.deals_init()
        for x in xrange(10):
            self.model.create_deal(aid, {'paper_id' : paid,
                                         'count' : 10,
                                         'direction' : -1,
                                         'points' : 100,
                                         'datetime' : datetime(2010, 10, 10)})
        self.model.make_positions(aid, paid)
                                     
        

    def test_calculate_positions(self, ):
        """
        """
        (mid, aid, paid) = self.deals_init()
        d = datetime(2000, 1, 1)
        net = 1000
        gross = 1000
        dds = []
        for x in xrange(0, 10):
            count = random.randint(1, 100)
            price = random.random() * 100 + 100
            direction = (random.random() > 0.5 and 1 or -1)
            for dirr in [direction, -direction]:
                for y in xrange(0, 10):
                    dds.append({"paper_id" : paid,
                                "count" : count,
                                "commission" : 0.1,
                                "direction" : dirr,
                                "datetime" : d,
                                "points" : price})
                    d += timedelta(0, random.randint(1, 7))
                    plg = dirr * count * price
                    gross += plg
                    net += plg - 0.1
        self.model.create_deal(aid, dds)
        self.model.make_positions(aid, paid)
        self.assertEqual(self.model._sqlite_connection.execute("select sum(count) from deals where direction > 0").fetchone()[0], self.model._sqlite_connection.execute("select sum(count) from deals where direction < 0").fetchone()[0])
        self.assertEqual(self.model._sqlite_connection.execute("select count(*) from positions_view").fetchone()[0], self.model._sqlite_connection.execute("select count(*) from positions").fetchone()[0])
        self.assertAlmostEqual(net, self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc limit 1", [aid, paid]).fetchone()[0])
        self.assertAlmostEqual(gross, self.model._sqlite_connection.execute("select gross_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc limit 1", [aid, paid]).fetchone()[0])
        
        
        d = datetime(2001, 1, 1, 0, 1)
        ndds = []
        for x in xrange(0, 10):
            count = random.randint(1, 100)
            price = random.random() * 100 + 100
            direction = (random.random() > 0.5 and 1 or -1)
            for dirr in [direction, -direction]:
                for y in xrange(0, 10):
                    ndds.append({"paper_id" : paid,
                                 "count" : count,
                                 "commission" : 0.1,
                                 "direction" : dirr,
                                 "datetime" : d,
                                 "points" : price})
                    d += timedelta(0, random.randint(1, 7))
                    plg = dirr * count * price
                    gross += plg
                    net += plg - 0.1
        self.model.create_deal(aid, ndds)
        self.model.make_positions(aid, paid)
        self.assertEqual(self.model._sqlite_connection.execute("select count(*) from positions_view").fetchone()[0], self.model._sqlite_connection.execute("select count(*) from positions").fetchone()[0])
        self.assertEqual(self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deals_view dv on dv.deal_id = d.id where d.direction > 0").fetchone()[0], self.model._sqlite_connection.execute("select sum(d.count) from deals d inner join deals_view dv on dv.deal_id = d.id where d.direction < 0").fetchone()[0])
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from deals where position_id is null").fetchone()[0])
        self.assertAlmostEqual(net, self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc limit 1", [aid, paid]).fetchone()[0])
        self.assertAlmostEqual(gross, self.model._sqlite_connection.execute("select gross_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc limit 1", [aid, paid]).fetchone()[0])

    def test_list_actions(self, ):
        """
        """
        self.model.dbinit()
        self.model.dbtemp()
        for x in xrange(0, 5):
            self.model.start_action("the action")
            self.model.create_money("{0}".format(x))
            self.model.end_action()
        # import pudb
        # pudb.set_trace()
        z = self.model.list_actions()
        self.assertEqual(5, len(z.fetchall()))
        

        
    def test_complex(self, ):
        """complex test simulating work with model by user interface 
        """
        self.model = sqlite_model.sqlite_model()
        self.model.create_new(":memory:")
        rubles = self.model.tacreate_money("RU")
        yens = self.model.tacreate_money("YEN")
        dollars = self.model.tacreate_money("USD")
        self.assertEqual(3, len(self.model.list_actions().fetchall()))
        self.assertTrue(rubles <> yens <> dollars <> None)
        ruacc = self.model.tacreate_account("test account with rubles", rubles, 1000)
        yenacc = self.model.tacreate_account("test account with yens", yens, 9000)
        dollac = self.model.tacreate_account("test account with dollars US", dollars, 100500)
        self.assertTrue(ruacc <> yenacc <> dollac <> None)
        sber = self.model.tacreate_paper("stock", "SBRF", 'MICEX')
        gaz = self.model.tacreate_paper("stock", "GAZP", 'MICEX')
        self.assertEqual(8, len(self.model.list_actions().fetchall()))
        def create_random_deals(date_start, stock, ballanced = True):
            ret = []
            d = copy(date_start)
            for x in xrange(0, random.randint(120, 150)):
                count1 = random.randint(10, 200)
                count2 = (ballanced and count1 or random.randint(10, 200))
                dir1 = (random.random() > 0.5 and 1 or -1)
                dir2 = (ballanced and -dir1 or (random.random() > 0.5 and 1 or -1))
                ret.append({"paper_id" : stock,
                            "count" : count1,
                            "direction" : dir1,
                            "points" : random.random() * 20 + 100,
                            "commission" : random.random(),
                            "datetime" : d})
                d += timedelta(0, random.randint(1, 10))
                ret.append({"paper_id" : stock,
                            "count" : count2,
                            "direction" : dir2,
                            "points" : random.random() * 20 + 100,
                            "commission" : random.random(),
                            "datetime" : d})
                d += timedelta(0, random.randint(1, 10))
            if ballanced:
                self.assertEqual(0, reduce(lambda a, b: a + b, map(lambda c: c["count"] * c["direction"], ret)))
            return ret
        
        x = create_random_deals(datetime(2010, 10, 10), sber)
        self.model.tacreate_deal(ruacc, x)
        xcount = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"] * c["points"], x)) - reduce(lambda a, b: a + b, map(lambda c: c["commission"], x))
        self.assertAlmostEqual(self.model.get_account(ruacc)["money_count"] + xcount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? and paper_id = ? order by datetime desc, id desc limit 1", [ruacc, sber]).fetchone()[0])
        self.model.tamake_positions(ruacc, sber)
        self.assertAlmostEqual(self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc, id desc limit 1", [ruacc, sber]).fetchone()[0],
                               self.model.get_account(ruacc)["money_count"] + xcount)
        a = self.model.list_actions().fetchall()
        self.assertEqual(10, len(a))
        self.model.go_to_action(a[0]["id"])
        self.assertEqual(0, self.model._sqlite_connection.execute("select count(*) from accounts").fetchone()[0])
        self.assertEqual(rubles, self.model._sqlite_connection.execute("select id from moneys limit 1").fetchone()[0])
        self.model.go_to_action(self.model._sqlite_connection.execute("select max(id) from hystory_steps").fetchone()[0])
        self.assertAlmostEqual(self.model.get_account(ruacc)["money_count"] + xcount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? and paper_id = ? order by datetime desc, id desc limit 1", [ruacc, sber]).fetchone()[0])
        self.assertAlmostEqual(self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? and paper_id = ? order by close_datetime desc, open_datetime desc, id desc limit 1", [ruacc, sber]).fetchone()[0],
                               self.model.get_account(ruacc)["money_count"] + xcount)
        
        y = create_random_deals(datetime(2010, 10, 10), gaz)
        ycount = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"] * c["points"], y)) - reduce(lambda a, b: a + b, map(lambda c: c["commission"], y))
        self.model.tacreate_deal(ruacc, y)
        self.model.tamake_positions(ruacc, gaz)
        self.assertAlmostEqual(self.model.get_account(ruacc)["money_count"] + xcount + ycount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ?  order by datetime desc, id desc limit 1", [ruacc]).fetchone()[0])
        self.assertAlmostEqual(self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? order by close_datetime desc, open_datetime desc, id desc limit 1", [ruacc]).fetchone()[0],
                               self.model.get_account(ruacc)["money_count"] + xcount + ycount)
        z = create_random_deals(datetime(2010, 10, 9), sber)
        zcount = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"] * c["points"], z)) - reduce(lambda a, b: a + b, map(lambda c: c["commission"], z))
        self.model.tacreate_deal(dollac, z)
        self.assertAlmostEqual(self.model.get_account(dollac)["money_count"] + zcount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? order by datetime desc, id desc limit 1", [dollac]).fetchone()[0])
        self.model.tacreate_point(sber, dollars, 10, 1)
        zpcount = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"] * c["points"] * 10, z)) - reduce(lambda a, b: a + b, map(lambda c: c["commission"], z))
        self.assertAlmostEqual(self.model.get_account(dollac)["money_count"] + zpcount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? order by datetime desc, id desc limit 1", [dollac]).fetchone()[0])
        self.assertAlmostEqual(self.model.get_account(dollac)["money_count"] + zpcount,
                               self.model._sqlite_connection.execute("select current_money from accounts_view where account_id = ?", [dollac]).fetchone()[0])
        self.assertEqual(len(z),
                         self.model._sqlite_connection.execute("select deals from accounts_view where account_id = ?", [dollac]).fetchone()[0])
        self.model.tamake_positions(dollac, sber)
        self.assertEqual(self.model._sqlite_connection.execute("select count(*) from positions where account_id = ?", [dollac]).fetchone()[0],
                         self.model._sqlite_connection.execute("select positions from accounts_view where account_id = ?", [dollac]).fetchone()[0])
        self.assertEqual(0,
                         self.model._sqlite_connection.execute("select count from account_ballance where account_id = ? and paper_id = ?", [dollac, sber]).fetchone()[0])
        self.assertEqual(0,
                         self.model._sqlite_connection.execute("select count from account_ballance where account_id = ? and paper_id = ?", [ruacc, sber]).fetchone()[0])
        self.assertEqual(0,
                         self.model._sqlite_connection.execute("select count from account_ballance where account_id = ? and paper_id = ?", [ruacc, gaz]).fetchone()[0])
        self.model.taremove_point(sber, dollars)
        self.assertAlmostEqual(self.model.get_account(dollac)["money_count"] + zcount,
                               self.model._sqlite_connection.execute("select net_after from deals_view where account_id = ? order by datetime desc, id desc limit 1", [dollac]).fetchone()[0])
        mu = create_random_deals(datetime(2010, 10, 11), gaz, ballanced = False)
        mucc = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"], mu))
        mucount = reduce(lambda a, b: a + b, map(lambda c: c["direction"] * c["count"] * c["points"], mu)) - reduce(lambda a, b: a + b, map(lambda c: c["commission"], mu))
        self.model.tacreate_deal(dollac, mu)
        self.assertAlmostEqual(self.model.get_account(dollac)["money_count"] + zcount + mucount,
                               self.model._sqlite_connection.execute("select current_money from accounts_view where account_id = ?", [dollac]).fetchone()[0])
        self.assertEqual(self.model._sqlite_connection.execute("select count from account_ballance where account_id = ? and paper_id = ?", [dollac, gaz]).fetchone()[0],
                         mucc)
        self.model.tamake_positions(dollac, gaz)
        if mucc <> 0:
            self.assertNotAlmostEqual(self.model.get_account(dollac)["money_count"] + zcount + mucount,
                                      self.model._sqlite_connection.execute("select net_after from positions_view where account_id = ? order by close_datetime desc, open_datetime desc, id desc limit 1", [dollac]).fetchone()[0])
        
    def test_create_position_from_data(self, ):
        """function create_position_from_data test
        """
        self.model.disconnect()
        self.model.create_new(':memory:')
        mid = self.model.tacreate_money('ru')
        aid = self.model.tacreate_account('superacc', mid, 1000)
        paid = self.model.tacreate_paper('stock', 'sber', 'micex')
        pid1 = self.model.tacreate_position_from_data(aid, {'paper_id' : paid,
                                                            'count' : random.randint(1, 100),
                                                            'direction' : (random.random() > 0.5 and 1 or -1),
                                                            'commission' : random.random(),
                                                            'open_datetime' : datetime(2010, 10, 10),
                                                            'close_datetime' : datetime(2010, 10, 11),
                                                            'open_points' : 50 + random.random() * 50,
                                                            'close_points' : 50 + random.random() * 50})
        self.assertEqual(2, self.model.assigned_account_deals(aid))
        self.assertEqual(1, self.model.assigned_account_positions(aid))
        pid2 = self.model.tacreate_position_from_data(aid, {'paper_id' : paid,
                                                            'count' : random.randint(1, 100),
                                                            'direction' : (random.random() > 0.5 and 1 or -1),
                                                            'commission' : random.random(),
                                                            'open_datetime' : datetime(2010, 11, 10),
                                                            'close_datetime' : datetime(2010, 11, 11),
                                                            'open_points' : 50 + random.random() * 50,
                                                            'close_points' : 50 + random.random() * 50})
        self.assertEqual(4, self.model.assigned_account_deals(aid))
        self.assertEqual(2, self.model.assigned_account_positions(aid))
        (accm, ) = self.model._sqlite_connection.execute('select net_after from positions_view order by close_datetime desc limit 1').fetchone()
        self.model._sqlite_connection.execute('delete from positions')
        self.model._sqlite_connection.execute('delete from positions_view')
        self.model.tamake_positions_for_whole_account(aid)
        (accm2, ) = self.model._sqlite_connection.execute('select net_after from positions_view order by close_datetime desc limit 1').fetchone()
        self.assertAlmostEqual(accm, accm2) # test if positions maked from deals are same again
        

if __name__ == '__main__':
    unittest.main()
