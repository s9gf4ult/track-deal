#!/bin/env python
# -*- coding: utf-8 -*-
## chart_tab_controller ##
from check_control import check_control
from select_control import select_control
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
        pg = self.notebook.get_current_page()
        if pg == 0:
            self.print_chart_0()
        elif pg == 1:
            self.print_chart_1()

    def print_chart_0(self, ):
        """\brief 
        """
        pass

    def print_chart_1(self, ):
        """\brief 
        """
        pass

        

