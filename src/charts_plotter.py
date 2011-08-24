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
        raise NotImplementedError()
