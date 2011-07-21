#!/bin/env python
# -*- coding: utf-8 -*-
## cairo_chart ##


import gtk
from common_drawer import common_drawer

class cairo_canva(gtk.DrawingArea):
    """\brief chart class to draw chart in window
    """
    def __init__(self, *args, **kargs):
        """\brief 
        """
        gtk.DrawingArea.__init__(self, *args, **kargs)
        self.connect('expose-event', self.expose)
        self._context = self.window.cairo_create()
        self._drawers = []

    def expose(self, widget, event):
        """\brief expose handler
        \param widget
        \param event
        """
        self._context.rectangle(event.area.x, event.area.y,
                                event.area.width, event.area.height)
        self._context.clip()
        self.redraw()
        return False

    def add_drawer(self, drawer):
        """\brief add instance of object performing draw action
        \param drawer - \ref common_drawer.common_drawer instance
        """
        assert(isinstance(drawer, common_drawer))
        self._drawers.append(drawer)

    def remove_drawer(self, drawer):
        """\brief remove drawer from the list
        \param drawer
        """
        ind = find_in_list(lambda obj: obj == drawer, self._drawers)
        if ind <> None:
            del self._drawers[ind]

    def redraw(self, ):
        """\brief call method 'draw' for all drawers added
        """
        rect = self.get_allocation()
        for drawer in self._drawers:
            drawer.draw(self._context, rect)
        
if __name__ == '__main__':
    from math import pi
    w = gtk.Dialog()
    p = w.get_content_area()
    class dummy(common_drawer):
        def draw(self, context, rect):
            rad = min(rect.height, rect.width) / 2.
            xc = rect.x + (rect.width / 2.)
            yc = rect.y + (rect.height / 2.)
            context.arc(xc, yc, rad, 0, 2 * pi)
            
    dr = dummy()
    canva = cairo_canva()
    canva.add_drawer(dr)
    p.pack_start(canva)
    w.show_all()
