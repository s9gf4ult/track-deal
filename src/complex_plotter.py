#!/bin/env python
# -*- coding: utf-8 -*-
## complex_plotter ##

from common_drawer import common_drawer
from od_exceptions import od_exception_parameter_error
from copy import copy

class complex_plotter(common_drawer):
    """\brief plotter which plot legend, mesh and charts
    """
    _data_charts = []
    
    def __init__(self, rectangle, legend = None, mesh = None, charts = None):
        """\brief constructor
        \param rectangle - \ref drawing_rectangle.drawing_rectangle instance
        \param legend - legend plotter object
        \param mesh - mesh plotter object
        \param charts - charts drawer
        """
        self._rectangle = rectangle
        self._legend = legend
        self._mesh = mesh
        self._charts = charts
        ## if true legend plot on top otherwise on the bottom
        self._legend_on_top = True

    def get_legend_on_top(self):
        """\brief Getter for property legend_on_top
        """
        return self._legend_on_top

    def set_legend_on_top(self, legend_on_top):
        """\brief Setter for property legend_on_top
        \param legend_on_top - bool
        """
        self._legend_on_top = legend_on_top
        
    def plot(self, data):
        """\brief add data to the plot drawer
        \param data \ref data_chart.data_chart instance
        """
        if len(self._data_charts) == 0:
            self._data_charts.append(data)
            self._rectangle.set_x_axis_type(data.get_x_exis_type())
            self._rectangle.set_y_axis_type(data.get_y_axis_type())
        else:
            xa = data.get_x_axis_type()
            ya = data.get_y_axis_type()
            rxa = self._rectangle.get_x_axis_type()
            rya = self._rectangle.get_y_axis_type()
            if xa != rxa:
                raise od_exception_parameter_error("x axis type must be {0} not {1}".format(rxa, xa))
            elif ya != rya:
                raise od_exception_parameter_error("y axis type must be {0} not {1}".format(rya, ya))
            else:
                self._data_charts.append(data)

    def autoscale(self, ):
        """\brief autoscale rectangle
        """
        self._rectangle.autoset_rectangle(self._data_charts)

    def flush(self, ):
        """\brief clean datacharts
        """
        self._data_charts = []

    def draw(self, context, rectangle):
        """\brief draw legend, mesh and charts
        \param context - cairo context
        \param rectangle - cairo context rectangle to draw
        """
        self._old_context = context
        self._old_rectangle = rectangle
        self._draw(context, rectangle)

    def _draw(self, context, rectangle):
        legend_height = self._determine_legend_height(context, rectangle)
        legend_rectangle = copy(rectangle)
        mesh_rectangle = copy(rectangle)
        if self._legend_on_top:
            legend_rectangle.height = legend_height
            mesh_rectangle.y += legend_height
            mesh_rectangle.height -= legend_height
        else:
            legend_rectangle.y += legend_rectangle.height - legend_height
            legend_rectangle.height = legend_height
            mesh_rectangle.height -= legend_height

        self._legend.draw(context, legend_rectangle)
        self._mesh.draw(context, mesh_rectangle)
        chart_rectangle = self._mesh.get_chart_area_rectangle()
        self._charts.draw(context, chart_rectangle)
                          
    def redraw(self, ):
        """\brief redraw with old context
        """
        self._draw(self._old_context, self._old_rectangle)
