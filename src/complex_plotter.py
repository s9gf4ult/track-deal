#!/bin/env python
# -*- coding: utf-8 -*-
## complex_plotter ##


class complex_plotter(common_drawer):
    """\brief plotter which plot legend, mesh and charts
    """
    def __init__(self, rectangle, legend = None, mesh = None, charts = None):
        """\brief constructor
        \param rectangle - 
        \param legend - legend plotter object
        \param mesh - mesh plotter object
        \param charts - charts drawer
        """
        self._legend = legend
        self._mesh = mesh
        self._charts = charts
        
