#!/bin/env python
# -*- coding: utf-8 -*-
## chart_tab_controller ##
from check_control import check_control
from select_control import select_control
from common_methods import show_error
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
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
        pass

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
        fig = plt.figure()
        ax = fig.add_subplot(111)
        names = map(lambda a: a[0], print_values)
        lines  = map(lambda chart: ax.plot_date(map(lambda chd: chd[0], chart[1]),
                                                map(lambda chy: chy[1], chart[1])), print_values)
        plt.figlegend(lines, names, 'upper left')
        
        majloc = AutoDateLocator()
        majform = AutoDateFormatter(majloc)
        ax.xaxis.set_major_locator(majloc)
        ax.xaxis.set_major_formatter(majform)
        ax.autoscale_view()
        ax.grid(True)
        fig.autofmt_xdate()
        fig.show()
