#!/bin/env python
# -*- coding: utf-8 -*-
## charts_plotter ##

from common_drawer import common_drawer

class charts_plotter(common_drawer):
    """\brief print just charts in selected rectangle
    """
    _data_charts = []
    _chart_rectangle = None

    def draw(self, context, rectangle):
        """\brief draw charts
        \param context - cairo context
        \param rectangle - cairo context rectangle
        """
        print('drawing charts')

    def set_data_charts(self, data_charts):
        """\brief Setter for property data_charts
        \param data_charts - list of \ref data_chart.data_chart instances
        """
        self._data_charts = data_charts

    def set_rectangle(self, rectangle):
        """\brief Setter for property rectangle
        \param rectangle
        """
        self._rectangle = rectangle
        
