#!/bin/env python
# -*- coding: utf-8 -*-
## open_ru_loader ##

from common_loader import common_loader
import sys
from xml.dom import minidom
from common_methods import reduce_by_string
import hashlib

class open_ru_loader(common_loader):
    """\brief loader for open.ru
    """
    def load(self, model, source):
        """\brief 
        \param model
        \param source
        """
        deals = self.get_deals(source)
        account_io = self.get_account_ios(source)
        repo_deals = self.get_repo_deals(source)
        if len(deals + repo_deals, account_io) == 0:
            sys.stderr.write('open_ru_loader: There is no one deal in the report {0}\n'.format(source.get_filename()))
            return True
        papers = []
        if source.get_load_repo():
            papers = self.get_papers(deals + repo_deals)
        else:
            papers = self.get_papers(deals)
            
        model.start_transacted_action('import {0} deals from report {1}'.format(len((deals + repo_deals if source.get_load_repo() else deals)),
                                                                                source.get_filename()))
        try:
            self.append_papers(model, papers)
            self.append_deals(model, deals, papers)
            if source.get_load_repo():
                self.append_deals(model, repo_deals, papers)
            if source.get_load_account_io():
                self.append_account_io(model, account_io)
        except Exception as e:
            model.rollback()
            raise e
        model.commit_transacted_action()

    def get_deals(self, source):
        """\brief return list of deal objects
        \param source - open_ru_source class instance
        """
        parsed = minidom.parse(source.get_filename())
        report_type = self.get_report_type(parsed)
        if report_type == 'forts':
            return self.get_forts_deals(parsed)
        elif report_type == 'micex':
            return self.get_micex_deals(parsed)
        else:
            raise assert("report type must be either 'forts' or 'micex'")

    def get_report_type(self, domparsed):
        """\brief determine type of report
        \param domparsed
        \retval "forts" if report type is forts
        \retval "micex" otherwise
        """
        rep = domparsed.getElementsByTagName('report')[0]
        deals = rep.getElementsByTagName('common_deal')[0].getElementsByTagName('item') # list of deals
        types = [a.getAttribute('security_type') for a in deals]
        if set(types) == set([u'Акции']):
            return 'micex'
        elif set(types) == set(['FUT']):
            return 'forts'
        else:
            raise Exception('wrong format of file: can not determine type of report')

    def get_forts_deals(self, domparsed):
        """\brief return list of deals for forts report type
        \param domparsed
        list of \ref report_deal objects
        """
        report = domparsed.getElementsByTagName('report')[0]
        deals = report.getElementsByTagName('common_deal')[0].getElementsByTagName('item')
        report_deals = []
        for deal in deals:
            d = report_deal()
            d.set_stock_name(deal.getAttribute('security_symb'))
            d.set_dtm(deal.getAttribute('deal_date'))
            d.set_points(deal.getAttribute('price'))
            d.set_count(deal.getAttribute('quantity'))
            d.set_direction(deal.getAttribute('deal_sign'))
            d.set_sha1(hashlib.sha1(reduce_by_string('', [deal.getAttribute(attrname) for attrname in
                                                          ['deal_date',
                                                           'security_name',
                                                           'expiration_date',
                                                           'price',
                                                           'quantity',
                                                           'order_number',
                                                           'deal_number',
                                                           'deal_sign']])).hexdigest())
            report_deal.append(d)
        

class report_deal(object):
    """\brief 
    """
    def __init__(self, ):
        self._stock_name = None
        self._dtm = None
        self._points = None
        self._count = None
        self._direction = None
        self._commission = None
        self._dbid = None
        self._attributes = None
        self._sha1 = None
    
    def set_stock_name(self, stock_name):
        """\brief Setter for property stock_name
        \param stock_name
        """
        assert(isinstance(stock_name, basestring))
        self._stock_name = stock_name

    def get_stock_name(self):
        """\brief Getter for property stock_name
        """
        return self._stock_name
    
    def set_dtm(self, dtm):
        """\brief Setter for property dtm
        \param dtm
        """
        if isinstance(dtm, basestring):
            self._dtm = datetime.strptime(dtm, '%Y-%m-%dT%H:%M:%S')
        elif isinstance(dtm, datetime):
            self._dtm = dtm

    def get_dtm(self):
        """\brief Getter for property dtm
        """
        return self._dtm
    
    def set_points(self, points):
        """\brief Setter for property points
        \param points
        """
        self._points = float(points)

    def get_points(self):
        """\brief Getter for property points
        """
        return self._points
    
    def set_count(self, count):
        """\brief Setter for property count
        \param count
        """
        self._count = int(count)

    def get_count(self):
        """\brief Getter for property count
        """
        return self._count

    def set_direction(self, direction):
        """\brief Setter for property direction
        \param direction
        """
        self._direction = int(direction)
        if self._direction not in [-1, 1]:
            raise Exception('direction must be just -1 or 1')

    def get_direction(self):
        """\brief Getter for property direction
        """
        return self._direction

    def set_commission(self, commission):
        """\brief Setter for property commission
        \param commission
        """
        self._commission = float(commission)

    def get_commission(self):
        """\brief Getter for property commission
        """
        return self._commission
    
    def set_dbid(self, dbid):
        """\brief Setter for property dbid
        \param dbid
        """
        self._dbid = dbid

    def get_dbid(self):
        """\brief Getter for property dbid
        """
        return self._dbid
    
    def set_attributes(self, attributes):
        """\brief Setter for property attributes
        \param attributes
        """
        assert(isinstance(attributes, dict))
        self._attributes = attributes

    def get_attributes(self):
        """\brief Getter for property attributes
        """
        return self._attributes

    def set_sha1(self, sha1):
        """\brief Setter for property sha1
        \param sha1
        """
        self._sha1 = unicode(sha1)
        
    def get_sha1(self):
        """\brief Getter for property sha1
        """
        return self._sha1

class report_paper(object):
    """\brief describes paper from deal
    """
    def __init__(self, ):
        self._name = None
        self._dbid = None
        self._market_name = None
        
    def set_market_name(self, market_name):
        """\brief Setter for property market_name
        \param market_name
        """
        self._market_name = market_name

    def get_market_name(self):
        """\brief Getter for property market_name
        """
        return self._market_name
    
    def set_name(self, name):
        """\brief Setter for property name
        \param name
        """
        self._name = name

    def get_name(self):
        """\brief Getter for property name
        """
        return self._name

    def set_dbid(self, dbid):
        """\brief Setter for property dbid
        \param dbid
        """
        self._dbid = dbid

    def get_dbid(self):
        """\brief Getter for property dbid
        """
        return self._dbid
