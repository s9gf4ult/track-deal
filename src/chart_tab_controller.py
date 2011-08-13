#!/bin/env python
# -*- coding: utf-8 -*-
## chart_tab_controller ##
from check_control import check_control
from select_control import select_control
from common_methods import show_error
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
from matplot_figure import matplot_figure as figure
from datetime import datetime, timedelta, date
import gtk

class chart_tab_controller(object):
    """\brief controller of tab "chart" of main window
    """
    def __init__(self, parent):
        """\brief constructor
        \param parent \ref gtk_view.gtk_view instance
        """
        self._parent = parent
        def shobject(name):
            return self._parent.window.builder.get_object(name)
        self.notebook = shobject('chart_notebook')
        self.chart0positions = select_control(answers = {'all' : shobject('chart_0_all'),
                                                         'filtered' : shobject('chart_0_filtered')})
        self.chart0net = shobject('chart_0_net')
        self.chart0gross = shobject('chart_0_gross')
        self.chart0profit = shobject('chart_0_profit')
        self.chart0loss = shobject('chart_0_loss')
        self.chart0cumulative_loss = shobject('chart_0_cumulative_loss')
        self.chart0cumulative_profit = shobject('chart_0_cumulative_profit')
        self.chart0use_withdraw = shobject('chart_0_use_withdraw')
        self.chart0gno = shobject('chart_0_group_no')
        self.chart0gday = shobject('chart_0_group_day')
        self.chart0gweek = shobject('chart_0_group_week')
        self.chart0gmonth = shobject('chart_0_group_month')
        
        self.chart1net = shobject('chart_1_net')
        self.chart1gross = shobject('chart_1_gross')
        self.chart1list = check_control(shobject('chart_1_accounts'),
                                        "",
                                        [['id', int], (u'Счет', gtk.CellRendererText())],
                                        select_button = shobject('chart_1_select'),
                                        deselect_button = shobject('chart_1_deselect'),
                                        reverse_button = shobject('chart_1_reverse'))
        shobject('print_charts').connect('activate', self.print_charts)
                                        

    def update(self, ):
        """\brief update list of accounts and may be more
        """
        if self._parent.connected():
            self.chart1list.update_rows(map(lambda a: (a['id'], a['name']), self._parent.model.list_accounts(['name'])), False)
            
    def print_charts(self, action):
        """\brief print charts handler
        \param action action instance
        """
        if not self._parent.connected():
            return
        pg = self.notebook.get_current_page()
        if pg == 0:
            self.print_chart_0()
        elif pg == 1:
            self.print_chart_1()

    def print_chart_0(self, ):
        cacc = self._parent.model.get_current_account()
        if cacc == None:
            return
        positions_data = None
        if self.chart0positions.get_value() == 'all':
            positions_data = self._parent.model.list_positions_view_with_condition('account_id = ?', [cacc['id']], order_by = ['close_datetime']).fetchall()
        elif self.chart0positions.get_value() == 'filtered':
            self._parent.positions_filter.update_filter()
            positions_data = self._parent.positions_filter.get_data(order_by = ['close_datetime'])
        if len(positions_data) == 0:
            return
        withdraw_data = []
        if self.chart0use_withdraw.get_active():
            withdraw_data = filter(lambda a: a['account_id'] == cacc['id'], self._parent.model.list_account_in_out().fetchall())
        
        retplot = []
        for (what, what_name, field_pl) in [(self.chart0net.get_active(), 'net', 'pl_net'),
                                            (self.chart0gross.get_active(), 'gross', 'pl_gross')]:
            if what:
                data = []
                wdp = 0
                psp = 0
                value = cacc['money_count']
                while psp < len(positions_data):
                    wd = (withdraw_data[wdp] if len(withdraw_data) > wdp else None)
                    ps = positions_data[psp]
                    if wd != None and wd['datetime'] <= ps['close_datetime']:
                        value += wd['money_count']
                        data.append((wd['datetime'], value))
                        wdp += 1
                        continue
                    else:
                        value += ps[field_pl]
                        data.append((ps['close_datetime'], value))
                        psp += 1
                data = self.group_if_need(data)
                retplot.append((what_name, data))

        if self.chart0profit.get_active():
            data = map(lambda a: (a['close_datetime'], a['pl_net']), filter(lambda c: c['pl_net'] >= 0, positions_data))
            data = self.sum_group_if_need(data)
            retplot.append(('profit', data))

        if self.chart0loss.get_active():
            data = map(lambda a: (a['close_datetime'], abs(a['pl_net'])), filter(lambda c: c['pl_net'] < 0, positions_data))
            data = self.sum_group_if_need(data)
            retplot.append(('loss', data))

        if self.chart0cumulative_profit.get_active():
            start = cacc['money_count']
            data = []
            for pst in positions_data:
                if pst['pl_net'] >= 0:
                    start += pst['pl_net']
                    data.append((pst['close_datetime'], start))
            data = self.group_if_need(data)
            retplot.append(('cum.profit', data))

        if self.chart0cumulative_loss.get_active():
            start = cacc ['money_count']
            data = []
            for pst in positions_data:
                if pst['pl_net'] < 0:
                    start += abs(pst['pl_net'])
                    data.append((pst['close_datetime'], start))
            data = self.group_if_need(data)
            retplot.append(('cum.loss', data))

        self.matplot_print(retplot)
        

    def print_chart_1(self, ):
        net = self.chart1net.get_active()
        gross = self.chart1gross.get_active()
        w = self._parent.window.builder.get_object('main_window')
        if not (net or gross):
            show_error(u'выберите что нибудь net или gross', w)
            return
        acclist = self.chart1list.get_checked_rows()
        if len(acclist) == 0:
            show_error(u'Выберите минимум один счет для печати', w)
            return
        
        retprint = []           # [('name', [(datetime, y_value)])]
        for (accid, accname) in acclist: # for each account
            positions_data = self._parent.model.list_positions_view_with_condition('account_id = ?', [accid], order_by = ['close_datetime']).fetchall()
            acc = self._parent.model.get_account(accid)
            if acc == None or len(positions_data) == 0:
                continue
            for (what, what_name, field_name) in [(net, 'net', 'net_after'),
                                                  (gross, 'gross', 'gross_after')]: # for net and gross
                if what:
                    name = u'{0} {1}'.format(accname, what_name)
                    data = map(lambda a: (a['close_datetime'], a[field_name]), positions_data)
                    data.insert(0, (positions_data[0]['close_datetime'], acc['money_count']))
                    retprint.append((name, data))
                    
        self.matplot_print(retprint)
            
    def matplot_print(self, print_values):
        """\brief print data by matplotlib and shw the figure
        \param print_values [(name - is a string, [(datetime, value)] - is a list of data to plot)] - list of charts to plot
        """
        if len(print_values) ==0:
            return
        fig = figure()
        ax = fig.add_subplot(111)
        names = map(lambda a: a[0], print_values)
        lines  = map(lambda chart: ax.plot_date(map(lambda chd: chd[0], chart[1]),
                                                map(lambda chy: chy[1], chart[1]), 'o-'), print_values)
        fig.legend(lines, names, 'upper left')
        
        majloc = AutoDateLocator()
        majform = AutoDateFormatter(majloc)
        ax.xaxis.set_major_locator(majloc)
        ax.xaxis.set_major_formatter(majform)
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()
        fig.show()

    def group_if_need(self, data):
        """\brief return the last elements of each group if grouping needed
        \param data list of tuples
        \return lit of tuples, 
        """
        if self.chart0gday.get_active():
            ret = self.group_by_day(data)
        elif self.chart0gweek.get_active():
            ret = self.group_by_week(data)
        elif self.chart0gmonth.get_active():
            ret = self.group_by_month(data)
        else:
            ret = data
        return ret

    def group_by_day(self, data):
        """\brief group data by day
        \param data list of tuples
        \return lit of tuples, grouped data
        """
        mindate = min(data, key = lambda a: a[0])[0].date()
        maxdate = max(data, key = lambda a: a[0])[0].date()
        d1 = timedelta(days = 1)
        crdate = mindate
        ret = []
        while crdate <= maxdate:
            carc = filter(lambda a: a[0].date() == crdate, data)
            if len(carc) == 0:
                crdate += d1
                continue
            arc = max(carc, key = lambda b: b[0])
            ret.append((crdate, arc[1]))
            crdate += d1
        return ret

    def group_by_week(self, data):
        """\brief group data by week
        \param data - list of tuples
        \return lit of tuples, grouped data
        """
        mindate = min(data, key = lambda a: a[0])[0].date()
        maxdate = max(data, key = lambda a: a[0])[0].date()
        week = (mindate - timedelta(days = mindate.weekday()))
        weekend = week + timedelta(days = 6)
        weekup = timedelta(days =7)
        ret = []
        while week <= maxdate:
            thisweek = filter(lambda a: week <= a[0].date() <= weekend, data)
            if len(thisweek) == 0:
                week += weekup
                weekend += weekup
                continue
            lastofweek = max(thisweek, key = lambda a: a[0])
            ret.append((weekend, lastofweek))
            week += weekup
            weekend += weekup
        return ret
        
    def group_by_month(self, data):
        """\brief group data by month
        \param data
        \return lit of tuples, grouped data
        """
        raise NotImplementedError()

    def sum_group_if_need(self, data):
        """\brief summ of data by grouping
        \param data
        \return lit of tuples, summarized data
        """
        ret = None
        if self.chart0gday.get_active():
            ret = self.sum_group_by_day(data)
        elif self.chart0gweek.get_active():
            ret = self.sum_group_by_week(data)
        elif self.chart0gmonth.get_active():
            ret = self.sum_group_by_month(data)
        else:
            ret = data
        return ret

    def sum_group_by_day(self, data):
        """\brief summ data of each day and return
        \param data
        \return list of tuples, grouped and summarized data
        """
        mindate = min(data, key = lambda a: a[0])[0].date()
        maxdate = max(data, key = lambda a: a[0])[0].date()
        d1 = timedelta(days = 1)
        crdate = mindate
        ret = []
        while crdate <= maxdate:
            carc = filter(lambda a: a[0].date() == crdate, data)
            if len(carc) == 0:
                crdate += d1
                continue
            arc = reduce(lambda a, b: a+b, map(lambda c: c[1], carc))
            ret.append((crdate, arc))
        return ret

    def sum_group_by_week(self, data):
        """\brief summ data of each week
        \param data
        """
        mindate = min(data, key = lambda a: a[0])[0].date()
        maxdate = max(data, key = lambda a: a[0])[0].date()
        week = (mindate - timedelta(days = mindate.weekday()))
        weekend = week + timedelta(days = 6)
        weekup = timedelta(days =7)
        ret = []
        while week <= maxdate:
            thisweek = filter(lambda a: week <= a[0].date() <= weekend, data)
            if len(thisweek) == 0:
                week += weekup
                weekend += weekup
                continue
            sumed = reduce(lambda a, b: a + b, map(lambda c: c[1], thisweek))
            ret.append((weekend, sumed))
            week += weekup
            weekend += weekup
        return ret

    def sum_group_by_month(self, data):
        """\brief summ data of each month
        \param data
        """
        raise NotImplementedError()

    
