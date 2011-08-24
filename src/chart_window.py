#!/bin/env python
# -*- coding: utf-8 -*-
## chart_window ##

import gtk
from cairo_canva import cairo_canva
from background_plotter import background_plotter
from legend_plotter import legend_plotter
from mesh_plotter import mesh_plotter
from charts_plotter import charts_plotter
from complex_plotter import complex_plotter

class chart_window(object):
    """\brief chart window controller and creator
    """
    def __init__(self, parent):
        self._parent = parent
        self.window = gtk.Dialog(title = "График", parent = self._parent.window.builder.get_object('main_window'), buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL))
        self.chart_area = cairo_canva()
        self.background = background_plotter()
        self.legend = legend_plotter()
        self.mesh = mesh_plotter()
        self.charts = charts_plotter()
        self.plotter = complex_plotter(legend = self.legend,
                                       mesh = self.mesh,
                                       charts = self.charts)
        self.chart_area.add_drawer(self.plotter)
        self.window.get_content_area().pack_start(self.chart_area, True, True)

    def show(self, ):
        """\brief show chart window
        """
        self.window.show_all()

    def plot(self, data):
        """\brief plot data in the chart area
        \param data - \ref data_chart.data_chart instance
        """
        self.plotter.plot(data)

    def redraw(self, ):
        self.plotter.draw()

    def set_background_color(self, color_string):
        """\brief set color of background
        \param color_string str, background color
        """
        self.background.set_color(color_string)

    def set_mesh_color(self, color_string):
        """\brief set color of the mesh
        \param color_string str, mesh color string
        """
        self.mesh.set_color(color_string)
        self.legend.set_color(color_string)

    def set_legend_font(self, font):
        """\brief set font for legend
        \param font
        """
        self.legend.set_font(font)

    def set_mesh_font(self, font):
        """\brief set font for mesh text prints
        \param font
        """
        self.mesh.set_font(font)

    def flush(self, ):
        """\brief delete all data before new plot
        """
        self.plotter.flush()
