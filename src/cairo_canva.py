#!/bin/env python
# -*- coding: utf-8 -*-
## cairo_chart ##


import gtk
from common_drawer import common_drawer
from common_methods import find_in_list

class cairo_canva(gtk.DrawingArea):
    """\brief chart class to draw chart in window
    """
    def __init__(self, *args, **kargs):
        """\brief 
        """
        gtk.DrawingArea.__init__(self, *args, **kargs)
        self.connect('expose-event', self.expose)
        self._drawers = []

    def expose(self, widget, event):
        """\brief expose handler
        \param widget
        \param event
        """
        self._context = self.window.cairo_create()
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
    import cairo
    from math import pi, sin
    from common_methods import map_to_context_coordinates
    from drawing_rectangle import drawing_rectangle
    from numpy import arange
    w = gtk.Window()
    w.connect('delete-event', gtk.main_quit)
    class dummy(common_drawer):
        def draw(self, context, rect):
            rad = min(rect.height, rect.width) / 2.
            xc = rect.x + (rect.width / 2.)
            yc = rect.y + (rect.height / 2.)
            context.set_source_rgb(0, 0, 0)
            context.arc(xc, yc, rad, 0, 2 * pi)
            context.fill()

    class dummy2(common_drawer):
        def draw(self, context, rect):
            width = rect.width / 3.
            height = rect.height / 3.
            xc = rect.x + width
            yc = rect.y + height
            context.set_source_rgb(1, 0, 0)
            context.set_line_width(3)
            context.rectangle(xc, yc, width, height)
            context.stroke()

    class sinus(common_drawer):
        def draw(self, context, rect):
            context.set_source_rgb(0.1, 0.5, 0)
            drc = drawing_rectangle(lower_x_limit=-10,
                                    upper_x_limit=10,
                                    lower_y_limit=-1,
                                    upper_y_limit=1)
            sin_data = map(lambda a: (a, sin(a)), arange(-10, 10, 0.1))
            mapsin = map_to_context_coordinates(drc, rect, sin_data)
            context.move_to(mapsin[0][0], mapsin[0][1])
            for dsin in mapsin[1:]:
                context.line_to(*dsin)
            context.stroke()

    class somefunc(common_drawer):
        def draw(self, context, rect):
            context.set_source_rgb(0.5, 0.5, 1)
            drc = drawing_rectangle(lower_x_limit = -10,
                                    upper_x_limit = 10,
                                    lower_y_limit = -10,
                                    upper_y_limit = 20)
            some_data = map(lambda a: (a, a ** 2 - 10), arange(-10, 10, 0.1))
            maped_data = map_to_context_coordinates(drc, rect, some_data)
            context.move_to(maped_data[0][0], maped_data[0][1])
            for dd in maped_data[1:]:
                context.line_to(dd[0], dd[1])
            context.stroke()

    dr2 = dummy2()
    dr = dummy()
    drsin = sinus()
    somedr = somefunc()
    canva = cairo_canva()
    canva.add_drawer(dr)
    canva.add_drawer(dr2)
    canva.add_drawer(drsin)
    canva.add_drawer(somedr)
    w.add(canva)
    w.show_all()
    gtk.main()
