#!/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import datetime
import hashlib
from exceptions import *


class common_source(object):
    """\brief common class for sources
    \par using:
    first initialize the object and open the source of deals, then pass this object to
    \ref common_model.common_model.
    
    
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

    def receive(self, ):
        """\brief get data from report
        \return list of hashes with papers and deals
        \verbatim
        name - string with name of stock
        class - class of the stock
        full-name - full name of stock if exists
        stock - the market name of the stock
        type - the type name 'action', 'future' or 'option'
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


class xml_parser(common_source):
    """
    \brief open.ru report parser
    parse and return deals in hash form
    """
    xml = None
    def __init__(self):
        pass

    def close(self, ):
        """\brief clear fields of the object
        """
        if hasattr(self, 'xml'):
            delattr(self, 'xml')
            delattr(self, 'filename')

    def get_action_name(self, ):
        """\brief return name of action to record in database
        """
        if not hasattr(self, 'xml'):
            raise od_exception(u'You must open file before getting action name')
        return u'import {0} deals from report {1}'.format(len(self.common_deals), self.filename)

    def open(self, filename):
        """\brief open the file with report
        \param filename - name of valid xml file with report
        """
        self.filename = filename
        self.xml = parse(filename)
        self.check_file()

    def receive(self):
        return self.common_deals

    def check_file(self):
        if not (self.xml.childNodes.length == 1 and self.xml.childNodes[0].nodeName == "report"):
            raise od_exception(u'There is no tag report')
        self.report = self.xml.childNodes[0]
        for name in ["common_deal", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise od_exception("there is no {0} in report or more that one found".format(name))
        cd = self.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
        ta = self.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
        self.total_account = ta
        if not (len(cd) > 0 and len(ta) > 1):
            raise od_exception(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        self.common_deals = []
        self.papers = []
        
        
        for cod in cd:                  # идем по тегам тега common_deals
            at = cod.attributes
            deal = {}
            dt = at.has_key('deal_time') and at['deal_time'].value or at['deal_date'].value
            deal['datetime'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
            for ( in ['security_type', 'security_name']:
                deal[cc] = at.has_key(cc) and at[cc].value
            for cc in ['price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds']:
                deal[cc] = at.has_key(cc) and float(at[cc].value) or 0
            if deal['volume'] == 0:
                deal['volume'] = deal['price'] * deal['quantity']
            rdata = reduce(lambda a, b: u'{0}{1}'.format(a, b), [deal['security_name'],
                                                                 deal['security_type'],
                                                                 deal['datetime'].isoformat(),
                                                                 deal['price'],
                                                                 deal['quantity'],
                                                                 deal['volume'],
                                                                 deal['deal_sign'],
                                                                 at['order_number'].value,
                                                                 at['deal_number'].value]).encode('utf-8')
            deal['sha1'] = hashlib.sha1(rdata).hexdigest()
            self.common_deals.append(deal)
            
        if self.report.attributes['board_list'].value.find('FORTS') >= 0: # если в атрибуте тега report присутствует слово FORTS то расписываем суммарную коммисию поровну по всем сделкам пропрорционально объему
            broker_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Вознаграждение Брокера', ta)[0].attributes['total_value'].value))
            stock_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Биржевой сбор', ta)[0].attributes['total_value'].value))
            summ_volume = sum(map(lambda a: a['volume'], self.common_deals))
            for deal in self.common_deals:
                deal['broker_comm'] = broker_comm / summ_volume * deal['volume']
                deal['stock_comm'] = stock_comm / summ_volume * deal['volume']
                
        self.checked=True

        
classes = {u'Отчет брокерского дома "Открытие"' : xml_parser}
