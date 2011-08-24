#!/bin/env python
# -*- coding: utf-8 -*-
## complex_plotter ##

from common_drawer import common_drawer
from od_exceptions import od_exception_parameter_error

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
        raise NotImplementedError()

    def redraw(self, ):
        """\brief redraw with old context
        """
        self._draw(self._old_context, self._old_rectangle)


    
