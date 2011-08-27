#!/bin/env python
# -*- coding: utf-8 -*-
## mesh_plotter ##

from common_drawer import common_drawer
from od_exceptions import od_exception
from cairo_rectangle import cairo_rectangle
from font_store import font_store

class mesh_plotter(common_drawer, font_store):
    """\brief draw mesh and rullers
    """
    _color = (0, 0, 0)
    ## instance of \ref drawing_rectangle.drawing_rectangle
    _rectangle = None
    _chart_area_rectangle = None
    _line_width = 1
    def draw(self, context, rectangle):
        """\brief draw the mesh
        \param context - cairo context
        \param rectangle - cairo context rectangle
        """
        fextent = self.get_font_extent(context)
        chartheight = rectangle.height - (2 * fextent[2]) - (4 * self._line_width)
        chartwidth = rectangle.width
        self._chart_area_rectangle = cairo_rectangle(rectangle.x, rectangle.y, chartwidth, chartheight)
        context.set_source_rgb(*self._color)
        context.set_line_width(self._line_width)
        context.rectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
        line1y = rectangle.y + chartheight
        line2y = line1y + fextent[2] + (2 * self._line_width)
        context.move_to(rectangle.x, line1y)
        context.line_to(rectangle.x + rectangle.width, line1y)
        context.move_to(rectangle.x, line2y)
        context.line_to(rectangle.x + rectangle.width, line2y)
        context.stroke()
        
    def set_line_width(self, line_width):
        """\brief Setter for property line_width
        \param line_width
        """
        self._line_width = line_width

    def get_line_width(self):
        """\brief Getter for property line_width
        """
        return self._line_width

    def set_color(self, color):
        """\brief Setter for property color
        \param color - tuple of three floats
        """
        self._color = color

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
