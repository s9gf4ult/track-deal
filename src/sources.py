#!/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import datetime
import hashlib
from od_exceptions import *
from common_methods import reduce_by_string
from copy import copy
from hashed_dict import hashed_dict
import math


class common_source(object):
    """\brief common class for sources
    \par using:
    first initialize the object and open the source of deals, then pass this object to
    \ref common_model.common_model.load_from_source method as parameter to load deals with papers into database
    """
    def __init__(self, ):
        """\brief 
        """
        pass

    def open(self, something):
        """\brief abstract method to open the source
        \param something
        """
        raise NotImplementedError()

    def receive_withdrawall(self, ):
        """\brief get data about account withdrawall operations
        \return list of hash tables with keys
        \c datetime - datetime\n
        \c money_count - float with amount of money to withdraw\n
        \c comment - str, if exists
        """
        raise NotImplementedError()

    def receive(self, ):
        """\brief get data from report
        \return list of hashes with papers and deals
        \verbatim
        name - string with name of stock
        class - class of the stock
        full-name - full name of stock if exists
        stock - the market name of the stock
        type - the type name 'stock', 'future' or 'option'
        deals - list of hashes with deals with keys:
                    sha1 - optional unique field
                    count - count of lots
                    direction - (-1) means BY, 1 means SELL
                    points - price in points
                    commission - commissions had worked in the currency (not in points, this is not very smart)
                    datetime - datetime.datetime instan
                    \endverbatim
        """
        raise NotImplementedError()

    def close(self, ):
        """\brief close data source
        """
        raise NotImplementedError()

    def get_action_name(self, ):
        """\brief return string with name of action
        \return string with name
        """
        raise NotImplementedError()


class open_ru_report_source(common_source):
    """
    \brief open.ru report parser
    parse and return deals in hash form
    """
    def __init__(self):
        self.xml = None
        self.papers = None
        self.nontrade_operations = None

    def close(self, ):
        """\brief clear fields of the object
        """
        if hasattr(self, 'xml'):
            delattr(self, 'xml')
            delattr(self, 'filename')

    def get_action_name(self, ):
        """\brief return name of action to record in database
        """
        if not hasattr(self, 'xml') or not hasattr(self, 'papers'):
            raise od_exception_report_error(u'You must open file before getting action name')
        return u'import {0} deals from report {1}'.format(len(self.papers), self.filename)

    def open(self, filename):
        """\brief open the file with report
        \param filename - name of valid xml file with report
        """
        self.filename = filename
        self.xml = parse(filename)
        self.check_file()

    def receive(self):
        return copy(self.papers)

    def receive_withdrawall(self, ):
        """\brief receive withdrawall
        """
        return self.nontrade_operations

    def check_file(self):
        if not (self.xml.childNodes.length == 1 and self.xml.childNodes[0].nodeName == "report"):
            raise od_exception_report_error(u'There is no tag report')
        self.report = self.xml.childNodes[0]
        for name in ["common_deal", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise od_exception_report_error("there is no {0} in report or more that one found".format(name))
        cd = self.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item") # list of 'item' elements in 'common_deal' tag
        ta = self.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item") # list of 'item' elements in 'account_totally_line' tag
        self.total_account = ta
        if not (len(cd) > 0 and len(ta) > 1):
            raise od_exception_report_error(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        attributes = map(lambda a: a.attributes, cd)
        report_type = set(map(lambda a: a['security_type'].nodeValue, attributes)) # all the posible 'security_type' attributes in the report
        if report_type == set(['FUT']): # if there is just 'FUT' type of the stock in the report
            prices = reduce(lambda a, b: a + b, # summary of prices for all deals
                            map(lambda b: float(b['price'].nodeValue), attributes))
            commission = reduce(lambda a, b: abs(float(a.attributes['total_value'].nodeValue)) +
                                abs(float(b.attributes['total_value'].nodeValue)), # sum of commission from 'account_totally_line' tag
                                filter(lambda c: c.attributes['total_description'].nodeValue in (u'Вознаграждение Брокера', u'Биржевой сбор'), ta))
            prices = commission / prices # now this is the commission value per one point
            self.papers = list(set(map(lambda a: hashed_dict({'name' : a['security_name'].nodeValue, # get unique paper records from the report
                                                              'type' : 'future',
                                                              'stock' : a['board_name'].nodeValue}), attributes)))
            for paper in self.papers: # fill each paper record with deals records
                deals = map(lambda a: {'sha1' : hashlib.sha1(reduce_by_string('', (a['deal_date'].nodeValue, a['security_name'].nodeValue, a['expiration_date'].nodeValue, a['price'].nodeValue, a['quantity'].nodeValue, a['order_number'].nodeValue, a['deal_number'].nodeValue, a['deal_sign'].nodeValue))).hexdigest(),
                                       'count' : math.trunc(float(a['quantity'].nodeValue)),
                                       'direction' : math.trunc(float(a['deal_sign'].nodeValue)),
                                       'points' : float(a['price'].nodeValue),
                                       'commission' : prices * float(a['price'].nodeValue), # this is because the commission is stored in 'total_account' tag of the report
                                       'datetime' : datetime.datetime.strptime(a['deal_date'].nodeValue, '%Y-%m-%dT%H:%M:%S')},
                            filter(lambda b: paper['name'] == b['security_name'].nodeValue and paper['stock'] == b['board_name'].nodeValue, attributes))
                paper['deals'] = deals
                
        elif report_type == set([u'Акции']): # if there is just 'Акции' type of the stock in the report
            self.papers = list(set(map(lambda a: hashed_dict({'name' : a['security_name'].nodeValue, # get unique paper records from the report
                                                              'stock' : a['board_name'].nodeValue,
                                                              'type' : 'stock'}),
                                       attributes)))
            repo_deals = self.report.getElementsByTagName('repo_deal')
            repo_attrs = None
            if len(repo_deals) == 1:
                repo = repo_deals[0].getElementsByTagName('item')
                repo_attrs = map(lambda a: a.attributes, repo)
                for repo1 in filter(lambda a: a['repo_part'].nodeValue == '1', repo_attrs):
                    for repo2 in filter(lambda a: a['repo_part'].nodeValue == '2' and a['grn_code'].nodeValue == repo1['grn_code'].nodeValue, repo_attrs):
                        repo2['deal_time'] = repo1['deal_time'].nodeValue
                        repo2['broker_comm'] = '0'
            
            for paper in self.papers: # fill each paper record with deal records
                deals = map(lambda a: {'sha1' : hashlib.sha1(reduce_by_string('', (a['deal_time'].nodeValue, a['security_name'].nodeValue, a['price'].nodeValue, a['quantity'].nodeValue, a['order_number'].nodeValue, a['deal_number'].nodeValue, a['deal_sign'].nodeValue, a['board_name'].nodeValue, a['broker_comm'].nodeValue, a['stock_comm'].nodeValue))).hexdigest(),
                                       'count' : math.trunc(float(a['quantity'].nodeValue)),
                                       'direction' : math.trunc(float(a['deal_sign'].nodeValue)),
                                       'points' : float(a['price'].nodeValue),
                                       'commission' : float(a['broker_comm'].nodeValue) + float(a['stock_comm'].nodeValue),
                                       'datetime' : datetime.datetime.strptime(a['deal_time'].nodeValue, '%Y-%m-%dT%H:%M:%S')},
                            filter(lambda b: paper['name'] == b['security_name'].nodeValue and paper['stock'] == b['board_name'].nodeValue, attributes))
                if repo_attrs != None:
                    try:
                        deals.extend(map(lambda a: {'sha1' : hashlib.sha1(reduce_by_string('', (a['deal_time'].nodeValue,
                                                                                                a['security_type'].nodeValue,
                                                                                                a['security_name'].nodeValue,
                                                                                                a['grn_code'].nodeValue,
                                                                                                a['deal_price'].nodeValue,
                                                                                                a['exec_sign'].nodeValue,
                                                                                                a['repo_part'].nodeValue,
                                                                                                a['quantity'].nodeValue,
                                                                                                'repo'))).hexdigest(),
                                                    'count' : math.trunc(float(a['quantity'].nodeValue)),
                                                    'direction' : math.trunc(float(a['exec_sign'].nodeValue)),
                                                    'points' : float(a['deal_price'].nodeValue),
                                                    'commission' : float(a['broker_comm'].nodeValue),
                                                    'datetime' : datetime.datetime.strptime(a['deal_time'].nodeValue, '%Y-%m-%dT%H:%M:%S'),
                                                    'user_attributes' : {'REPO' : a['repo_part'].nodeValue}},
                                         filter(lambda b: b['security_name'].nodeValue == paper['name'], repo_attrs)))
                    except Exception:
                        pass    # FIXME! we must do something here
                paper['deals'] = deals
            nontrade = self.report.getElementsByTagName('nontrade_money_operation')
            if len(nontrade) == 1:
                nt = nontrade[0].getElementsByTagName('item')
                nontrade_attrs = map(lambda a: a.attributes, nt)
                self.nontrade_operations = map(lambda a: {'datetime' : datetime.datetime.strptime(a['operation_date'].nodeValue, '%Y-%m-%dT%H:%M:%S'),
                                                          'sha1' : hashlib.sha1(reduce_by_string('', (a['operation_date'].nodeValue, a['amount'].nodeValue, a['comment'].nodeValue, a['ground'].nodeValue))).hexdigest(),
                                                          'money_count' : float(a['amount'].nodeValue),
                                                          'comment' : a['comment'].nodeValue},
                                               nontrade_attrs)
        else:
            raise od_exception_report_error('This report is strange, dont know what type of report is it futures or stocks ?')
        
        
classes = {u'Отчет брокерского дома "Открытие"' : open_ru_report_source} # this is global variable using to store name and class of importer
