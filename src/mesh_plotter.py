#!/bin/env python
# -*- coding: utf-8 -*-
## mesh_plotter ##

from common_drawer import common_drawer

class mesh_plotter(common_drawer):
    """\brief draw mesh and rullers
    """
    _color = (0, 0, 0)
    _rectangle = None
    def draw(self, context, rectangle):
        """\brief draw the mesh
        \param context - cairo context
        \param rectangle - cairo context rectangle
        """
        raise NotImplementedError()

    def set_color(self, color):
        """\brief Setter for property color
        \param color - tuple of three floats
        """
        self._color = color

    def set_font(self, font):
        """\brief set font for mesh text drawings
        \param font - str, font description string
        """
        raise NotImplementedError()

    def set_rectangle(self, rectangle):
        """\brief Setter for property rectangle
        \param rectangle - \ref drawing_rectangle.drawing_rectangle instance
        """
        self._rectangle = rectangle
        
