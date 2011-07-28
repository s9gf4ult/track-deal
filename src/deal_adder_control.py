#!/bin/env python
# -*- coding: utf-8 -*-
from datetime_control import *
from combo_control import *
from number_range_control import number_control
from time_control import *
from select_control import *
from combo_select_control import *
from common_methods import *
from attributes_control import *
import gtk_view
import sys

class deal_adder_control:
    """\brief control for dialog for adding or editing one deal
    """
    def __init__(self, parent):
        """
        \param parent \ref gtk_view.gtk_view instance
        """
        assert(isinstance(parent, gtk_view.gtk_view))
        self.builder = make_builder('glade/deal_adder.glade')
        self._parent = parent
        def shorter(name):
            return self.builder.get_object("deal_adder_{0}".format(name))
        w = self.builder.get_object("deal_adder")
        w.set_transient_for(self._parent.window.builder.get_object('main_window'))
        w.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.datetime = datetime_control(shorter("calendar"),
                                         time_control(shorter("hour"),
                                                      shorter("min"),
                                                      shorter("sec")),
                                         year = shorter("year"),
                                         month = shorter("month"),
                                         day = shorter("day"))
        self.account = combo_select_control(shorter("account"))
        self.instrument = combo_select_control(shorter("instrument"))
        # self.market = combo_control(shorter("market"))
        self.price = number_control(shorter("price"), step_incr = 0.1, digits = 4)
        self.price.set_lower_limit(0)
        self.price.set_upper_limit(sys.float_info.max)
        self.count = number_control(shorter("count"))
        self.count.set_lower_limit(0)
        self.count.set_upper_limit(sys.maxint)
        self.direction = select_control({ -1 : shorter("buy_rb"),
                                          1 : shorter("sell_rb")})
        self.commission = number_control(shorter("comm"), step_incr = 0.1, digits = 4)
        self.commission.set_lower_limit(0)
        self.commission.set_upper_limit(sys.float_info.max)
        self.attributes = attributes_control(shorter("attributes"), shorter("attr_name"), shorter("attr_val"), shorter("attr_add"), shorter("attr_del"))

    def run(self):
        """
        \brief run the dialog
        \retval gtk.RESPONSE_CANCEL if cancel pressed
        \retval gtk.RESPONSE_ACCEPT if save pressed
        """
        w = self.builder.get_object("deal_adder")
        w.show_all()
        ret = w.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if not self.check_correctness():
                ret = w.run()
            else:
                w.hide()
                return ret
        w.hide()
        return ret

    def get_data(self):
        """
        \return hash table with keys:\n
        \c datetime\n
        \c paper_id - id of paper\n
        \c points - price in points\n
        \c count - count of contracts\n
        \c direction - (-1) or 1\n
        \c commission\n
        \c account_id selected account\n
        \c attributes - hash table like {name : value}
        """
        return {"datetime" : self.datetime.get_datetime(),
                "paper_id" : self.instrument.get_value(),
                "points" : self.price.get_value(),
                "count" : self.count.get_value(),
                "direction" : self.direction.get_value(),
                "commission" : self.commission.get_value(),
                "account_id" : self.account.get_value(),
                "user_attributes" : self.attributes.get_attributes()}

    def load_from_deal(self, data):
        """\brief load data from deal into widget
        \param data - int, deal id
        """
        if not self._parent.connected():
            return
        d = self._parent.model.get_deal(data)
        if d == None:
            return
        for (setter, key) in [(self.datetime.set_datetime, "datetime"),
                              (self.direction.set_value, "direction"),
                              (self.account.set_value, "account_id"),
                              (self.instrument.set_value, "paper_id"),
                              (self.price.set_value, "points"),
                              (self.count.set_value, "count"),
                              (self.commission.set_value, "commission"),
                              (self.attributes.set_attributes, "user_attributes")]:
            m = gethash(d, key)
            if m != None:
                setter(m)

    def flush_attributes(self):
        self.attributes.flush()
        

    def check_correctness(self):
        """\brief check if all data inserted correctly
        \retval True all data corect
        \retval False some data incorrect

        When checking, displey message about input mistakes if exists
        """
        mss = []
        if self.account.get_value() == None:
            mss.append(u'Вы должны указать счет')
        if self.instrument.get_value() == None:
            mss.append(u'Вы должны указать инструмент')
        if self.price.get_value() <= 0:
            mss.append(u'Вы должны указать цену контракта')
        if self.count.get_value() <= 0:
            mss.append(u'вы должны указать количество котрактов')
        if len(mss) > 0:
            show_error(reduce(lambda a, b: u'{0}\n{1}'.format(a, b), mss), self.builder.get_object("deal_adder"))
            return False
        else:
            return True

    # def update_widget(self, security_names, security_types, accounts = None):
    #     self.instrument.update_widget(security_names)
    #     self.market.update_widget(security_types)
    #     self.account.update_answers(accounts, none_answer = -1)

    def set_current_datetime(self):
        """\brief set current datetime to datetime widget
        """
        self.datetime.set_current_datetime()

    def reset_fields(self, ):
        """\brief clean all fields
        """
        self.account.update_answers([], -1)
        self.account.set_value(-1)
        self.instrument.update_answers([], -1)
        self.instrument.set_value(-1)
        self.count.set_value(0)
        self.price.set_value(0)
        self.commission.set_value(0)
        self.direction.set_value(-1)

    def update_adder(self, ):
        """\brief update posible values for account and instrument widget
        """
        if not self._parent.connected():
            return
        papers = self._parent.model.list_papers(["name"]).fetchall()
        pps = map(lambda p: (p["id"], p["name"]), papers)
        self.instrument.update_answers(pps)
        accs = self._parent.model.list_accounts(["name"]).fetchall()
        acs = map(lambda ac: (ac["id"], ac["name"]), accs)
        self.account.update_answers(acs)
        if is_null_or_empty(self.account.get_value()):
            cacc = self._parent.model.get_current_account()
            if cacc <> None:
                self.account.set_value(cacc['id'])
        
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = deal_adder_control(b)
    print(con.run())
