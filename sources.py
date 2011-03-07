#!/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import datetime


class xml_parser():
    def __init__(self, filename):
        self.xml = parse(filename)
        self.checked = False

    def check_file(self):
        if not (self.xml.childNodes.length == 1 and self.xml.childNodes[0].nodeName == "report"):
            raise Exception(u'Нет тега report')
        self.report = self.xml.childNodes[0]
        for name in ["common_deal", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise Exception("there is no {0} in report or more that one found".format(name))
        cd = self.report.getElementsByTagName("common_deal")[0].getElementsByTagName("item")
        ta = self.report.getElementsByTagName("account_totally_line")[0].getElementsByTagName("item")
        #self.briefcase = self.report.getElementsByTagName("briefcase_position")[0].getElementsByTagName("item")
        if not (len(cd) > 0 and len(ta) > 1):
            raise Exception(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        self.common_deals = []
        for cod in cd:
            at = cod.attributes
            deal = {}
            dt = at.has_key('deal_time') and at['deal_time'].value or at['deal_date'].value
            deal['datetime'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
            for cc in ['security_type', 'security_name', 'grn_code']:
                deal[cc] = at.has_key(cc) and at[cc].value
            for cc in ['price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds']:
                deal[cc] = at.has_key(cc) and float(at[cc].value) or 0
            self.common_deals.append(deal)
        self.checked=True
