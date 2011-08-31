#!/bin/env python
# -*- coding: utf-8 -*-
## font_store ##

from common_methods import describe_font_cairo

class font_store(object):
    """\brief font storer
    """
    _family = None
    _size = None
    _slant = None
    _weight = None

    def get_text_height(self, context):
        """\brief return text height
        \param context - cairo context
        \return float - height of text
        """
        return self.get_font_extent(context)[2]

    def set_font(self, font):
        """\brief set font
        \param font - str font description string
        """
        (self._family, self._slant, self._weight, self._size) = describe_font_cairo(font)

    def get_font_extent(self, context):
        """\brief return tuple of 5 elements
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        return context.font_extents()

    def chose_current_font(self, context):
        """\brief 
        \param context - cairo context
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
