#!/bin/env python
# -*- coding: utf-8 -*-
## matplot_figure ##

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import gtk

class matplot_figure(object):
    """\brief figure to show, which can be closed
    """
    def __init__(self, ):
        """\brief constuctor
        """
        self.win = gtk.Window()
        self.win.connect("delete-event", lambda widget, event: False)
        self.win.set_default_size(640,480)
        self.win.set_title("Plot")
        vbox = gtk.VBox()
        self.win.add(vbox)
        self.fig = Figure(figsize=(5,4), dpi=100)
        
        canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
        vbox.pack_start(canvas)
        toolbar = NavigationToolbar(canvas, self.win)
        vbox.pack_start(toolbar, False, False)

    def show(self, ):
        """\brief show window of the figure
        """
        self.win.show_all()

    def hide(self, ):
        """\brief hide window of the figure
        """
        self.win.hide()

    def add_subplot(self, *args, **kargs):
        """\brief 
        \param *args
        \param **kargs
        """
        return self.fig.add_subplot(*args, **kargs)

    def autofmt_xdate(self, *args, **kargs):
        """\brief autoformat date along X
        \param *args
        \param **kargs
        """
        return self.fig.autofmt_xdate(*args, **kargs)
