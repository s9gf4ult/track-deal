#!/bin/env python
# -*- coding: utf-8 -*-
## data_chart ##

from copy import copy
from od_exceptions import od_exception

class data_chart(object):
    """\brief object keeping the data of chart
    """
    def __init__(self, data_list, color = (0, 0, 0), legend = '', line_width = 1):
        """
        \param data_list list of tuples with data (X axis data, Y axis data)
        \param color = tuple with 3 float elements
        \param legend = string with name
        \param line_width = width of line to draw
        """
        self.set_data_list(data_list)
        self.set_color(color)
        self.set_legend(legend)
        self.set_line_width(line_width)
        
    def get_data_list(self):
        """\brief Getter for property data_list
        """
        return self._data_list

    def set_data_list(self, data_list):
        """\brief Setter for property data_list
        \param data_list - list of tuples of two elements
        """
        if not isinstance(data_list, list):
            raise ValueError('data list must be list')
        for elt in data_list:
            assert len(elt) == 2
        self._data_list = copy(data_list)
        self._data_list.sort(lambda a, b: cmp(a[0], b[0]))

    def append_data(self, data):
        """\brief append data to data list and resort it
        \param data tuple with data or list of tuples
        """
        if isinstance(data, tuple):
            assert len(data) == 2
            self._data_list.append(data)
        elif isinstance(data, list):
            for elt in data:
                assert len(elt) == 2
            self._data_list.extend(data)
        else:
            raise ValueError('data must be tuple or list')
        self._data_list.sort()
        
    def set_legend(self, legend):
        """\brief Setter for property legend
        \param legend
        """
        self._legend = legend

    def get_legend(self):
        """\brief Getter for property legend
        """
        return self._legend
    
    def set_color(self, color):
        """\brief Setter for property color
        \param color
        """
        if len(color) <> 3:
            raise ValueError('color must be 3 element tuple')
        self._color = tuple(map(lambda a: float(a), color))

    def get_color(self):
        """\brief Getter for property color
        """
        return self._color
    
    def get_drawing_rectangle(self, ):
        """\brief Get rectangle in which data is
        \return tuple of 4 elemnts (min_x, max_x, min_y, max_y)
        """
        (x_values, y_values) = zip(*self.get_data_list())
        return (min(x_values), max(x_values), min(y_values), max(y_values))

    def set_line_width(self, line_width):
        """\brief Setter for property line_width
        \param line_width
        """
        self._line_width = float(line_width)

    def get_line_width(self):
        """\brief Getter for property line_width
        """
        return self._line_width
    
    def get_x_axis_type(self, ):
        """\brief return type of axis X
        """
        if len(self._data_list) == 0:
            raise od_exception(u'you must specify some data to get X type')
        return type(self._data_list[0][0])

    def get_y_axis_type(self, ):
        """\brief return type of Y axis
        """
        if len(self._data_list) == 0:
            raise od_exception(u'you must specify some data to get Y type')
        t = type(self._data_list[0][1])
        return (float if t == int or t == float else t)

