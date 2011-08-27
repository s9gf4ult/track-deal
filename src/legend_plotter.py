#!/bin/env python
# -*- coding: utf-8 -*-
## legend_plotter ##

from common_drawer import common_drawer
from common_methods import describe_font_cairo
from od_exceptions import od_exception
from math import trunc
import pango

class legend_plotter(common_drawer):
    """\brief plot legend
    """
    _family = None
    _size = None
    _slant = None
    _weight = None
    ## color of the text
    _color = (0, 0, 0)                 
    ## list of tuples (text, color) where color is tuple of 3 floats
    # color determines the color of small scuare left of the text
    _strings = []
    def draw(self, context, rectangle):
        """\brief draw legend of cairo context
        \param context - cairo context
        \param rectangle - cairo context rectangle to draw
        """
        textheight = self._get_text_height(context)
        colons, lines = self._get_colons_and_lines(context, textheight, rectangle.width)
        width = rectangle.width / colons
        for strindx in xrange(0, len(self._strings)):
           colon = strindx % colons
           line = trunc(strindx / colons)
           x = colon * width + rectangle.x
           y = line * textheight * 4. / 3. + rectangle.y # 4/3 is because of some additional space between lines in 1/3 of line height
           self._draw_legend_element(context, x, y, self._strings[strindx])
           
    def _draw_legend_element(self, context, x, y, element):
        """\brief draw small colour square and text right of it
        \param context - cairo context
        \param x - float, horizontal position of the left top corner of the element
        \param y - float, vertical positions of the left top corner of the element
        \param element - tuple of string and tuple of 3 floats, string and color of square
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        extent = context.font_extents()
        context.set_source_rgb(*element[1])
        context.rectangle(x, y, extent[2], extent[2]) # extent[2] is height of text
        context.fill()
        context.set_source_rgb(*self._color)
        context.move_to(x + 1.5 * extent[2], y + extent[0]) # extent[0] is ascend of text
        context.show_text(element[0])
        context.stroke()

    def set_color(self, color):
        """\brief Setter for property color
        \param color - tuple of three floats
        """
        self._color = color
        
    def set_font(self, font):
        """\brief set font
        \param font - str font description string
        """
        (self._family, self._slant, self._weight, self._size) = describe_font_cairo(font)

    def calculate_height(self, context, width):
        """\brief calculate height with given width
        \param context - cairo context
        \param width - float, width in which to fit legend
        """
        if self._family == None:
            raise od_exception('you must specify font before calculating its height')
        textheight = self._get_text_height(context)
        colons, lines = self._get_colons_and_lines(context, textheight, width)
        return lines * textheight + ((lines - 1) * textheight / 3.) # lines + space between lines (1/3 of line height)

    def _get_colons_and_lines(self, context, textheight, width):
        """\brief return colons and lines to fit text in
        \param context - cairo context
        \param textheight - height of the text
        \param width - width to fit text in
        \return tuple of colons and lines
        """
        maxtextwidth = self._get_max_text_width(context)
        maxtextwidth += 1.5 * textheight # this is because we draw small color scuare left of the text
        colons = trunc(width / maxtextwidth) # how much colons can be placed
        colons = 1 if colons == 0 else colons
        lines = trunc(len(self._strings) / colons)
        lines += (0 if len(self._strings) % colons == 0 else 1)
        return colons, lines
        
    def _get_max_text_width(self, context):
        """\brief return maximum height width
        \param context - cairo context
        \return float - text width in context coordinates
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        ret = 0
        for string in self._strings:
            ret = max(ret, context.text_extents(string[0])[2])
        return ret

    def _get_text_height(self, context):
        """\brief return text height
        \param context - cairo context
        \return float - height of text
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        return context.font_extents()[2]

    def set_strings(self, strings):
        """\brief Setter for property strings
        \param strings - list of tuples of string and tuple of 3 floats
        """
        self._strings = strings
        
