#!/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import datetime
import hashlib


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
        self.total_account = ta
        if not (len(cd) > 0 and len(ta) > 1):
            raise Exception(u'Странное количество тегов item в отчете, либо отчет битый, либо это вобще не отчет')
        self.common_deals = []
        for cod in cd:                  # идем по тегам тега common_deals
            at = cod.attributes
            deal = {}
            dt = at.has_key('deal_time') and at['deal_time'].value or at['deal_date'].value
            deal['datetime'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')
            for cc in ['security_type', 'security_name', 'grn_code']:
                deal[cc] = at.has_key(cc) and at[cc].value
            for cc in ['price', 'quantity', 'volume', 'deal_sign', 'broker_comm', 'broker_comm_nds', 'stock_comm', 'stock_comm_nds']:
                deal[cc] = at.has_key(cc) and float(at[cc].value) or 0
            if deal['volume'] == 0:
                deal['volume'] = deal['price'] * deal['quantity']
            deal['sha1'] = hashlib.sha1(reduce(lambda a, b: u'{0}{1}'.format(a, b), [deal['security_name'],
                                                                                     deal['security_type'],
                                                                                     deal['datetime'].isoformat(),
                                                                                     deal['price'],
                                                                                     deal['quantity'],
                                                                                     deal['volume'],
                                                                                     deal['deal_sign'],
                                                                                     at['order_number'],
                                                                                     at['deal_number']]).encode('utf-8')).hexdigest()
            self.common_deals.append(deal)
            
        if self.report.attributes['board_list'].value.find('FORTS') >= 0: # если в атрибуте тега report присутствует слово FORTS то расписываем суммарную коммисию поровну по всем сделкам пропрорционально объему
            broker_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Вознаграждение Брокера', ta)[0].attributes['total_value'].value))
            stock_comm = abs(float(filter(lambda a: a.attributes['total_description'].value == u'Биржевой сбор', ta)[0].attributes['total_value'].value))
            summ_volume = sum(map(lambda a: a['volume'], self.common_deals))
            for deal in self.common_deals:
                deal['broker_comm'] = broker_comm / summ_volume * deal['volume']
                deal['stock_comm'] = stock_comm / summ_volume * deal['volume']
                
        self.checked=True
