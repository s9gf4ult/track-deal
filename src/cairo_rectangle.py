#!/bin/env python
# -*- coding: utf-8 -*-
## cairo_rectangle ##

class cairo_rectangle(object):
    """\brief 
    """
    def __init__(self, x, y, width, height):
        """\brief 
        \param x
        \param y
        \param width
        \param height
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
def copy_cairo_rectangle(rectangle):
    """\brief return \ref cairo_rectangle.cairo_rectangle object copied from initial rectangle
    \param rectangle
    """
    return cairo_rectangle(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
