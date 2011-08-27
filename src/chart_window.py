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
from drawing_rectangle import drawing_rectangle

class chart_window(object):
    """\brief chart window controller and creator
    """
    def __init__(self, parent):
        self._parent = parent
        self.window = gtk.Dialog(title = "График", buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL))
        if self._parent != None:
            self.window.set_transient_for(self._parent.window.builder.get_object('main_window'))
            self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            self.window.set_position(gtk.WIN_POS_CENTER)
        self.chart_area = cairo_canva()
        self.background = background_plotter()
        self.legend = legend_plotter()
        self.mesh = mesh_plotter()
        self.charts = charts_plotter()
        self.rectangle = drawing_rectangle()
        self.plotter = complex_plotter(self.rectangle,
                                       legend = self.legend,
                                       mesh = self.mesh,
                                       charts = self.charts)
        self.chart_area.add_drawer(self.background)
        self.chart_area.add_drawer(self.plotter)
        self.window.get_content_area().pack_start(self.chart_area, True, True)
        self.window.set_default_size(640, 480)

    def show(self, ):
        """\brief show chart window
        """
        self.window.show_all()

    def plot(self, data):
        """\brief plot data in the chart area
        \param data - \ref data_chart.data_chart instance
        """
        self.plotter.plot(data)

    def autoscale(self, ):
        """\brief scale rectangle when data already ploted
        """
        self.plotter.autoscale()

    def redraw(self, ):
        self.plotter.redraw()

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

    def set_legend_on_top(self, legend_on_top):
        """\brief if true legend rawing on top
        \param legend_on_top
        """
        self.plotter.set_legend_on_top(legend_on_top)

    def get_legend_on_top(self, ):
        """\brief return true if legend drawing on top
        """
        return self.plotter.get_legend_on_top()

if __name__ == '__main__':
    from datetime import datetime
    from random import random
    from data_chart import data_chart
    win = chart_window(None)
    x = [datetime(2010, 10, 10), datetime(2010,10, 11), datetime(2010, 10, 12)]
    ys = []
    colors = []
    for i in xrange(7):
        pk = []
        for j in xrange(3):
            pk.append(random())
        ys.append(pk)
        colors.append((random(), random(), random()))
    legends = ['every', 'hunter', 'whant', 'to know', 'where', 'pheasant', 'is sitting']
    data_charts = []
    for i in xrange(7):
        data_charts.append(data_chart(zip(x, ys[i]), color = colors[i], legend = legends[i], line_width = 1.5))

    win.set_legend_font('Terminus 20')
    win.set_mesh_font('Terminus 20')
    win.set_background_color((0, 0, 0))
    win.set_mesh_color((1, 1, 1))
    for dd in data_charts:
        win.plot(dd)
    win.autoscale()
    win.mesh.set_line_width(2)
    win.show()
    win.window.run()
