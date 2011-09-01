#!/bin/env python
# -*- coding: utf-8 -*-
## background_plotter ##

from common_drawer import common_drawer

class background_plotter(common_drawer):
    """\brief print rectangle with one color
    """
    def __init__(self, ):
        super(background_plotter, self).__init__()
        self._color = (0, 0, 0)
        
    def set_color(self, color):
        """\brief set background color
        \param color - tuple of three float numbers from 0 to 1
        """
        self._color = color

    def draw(self, context, rectangle):
        context.set_source_rgb(*self._color)
        context.rectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
        context.fill()
