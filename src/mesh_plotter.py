#!/bin/env python
# -*- coding: utf-8 -*-
## mesh_plotter ##

from common_drawer import common_drawer
from od_exceptions import od_exception
from copy import copy

class mesh_plotter(common_drawer):
    """\brief draw mesh and rullers
    """
    _color = (0, 0, 0)
    ## instance of \ref drawing_rectangle.drawing_rectangle
    _rectangle = None
    _chart_area_rectangle = None
    def draw(self, context, rectangle):
        """\brief draw the mesh
        \param context - cairo context
        \param rectangle - cairo context rectangle
        """
        self._chart_area_rectangle = copy(rectangle)
        print('drawing mesh')

    def set_color(self, color):
        """\brief Setter for property color
        \param color - tuple of three floats
        """
        self._color = color

    def set_font(self, font):
        """\brief set font for mesh text drawings
        \param font - str, font description string
        """
        print(u'setting font {0} for mesh'.format(font))
        
    def set_rectangle(self, rectangle):
        """\brief Setter for property rectangle
        \param rectangle - \ref drawing_rectangle.drawing_rectangle instance
        """
        self._rectangle = rectangle
        
    def get_chart_area_rectangle(self, ):
        """\brief return rectangle of the chart area in cairo context
        """
        if self._chart_area_rectangle == None:
            raise od_exception('you must call draw, then get chart area rectangle')
        return self._chart_area_rectangle
