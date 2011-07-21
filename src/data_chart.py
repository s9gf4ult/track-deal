#!/bin/env python
# -*- coding: utf-8 -*-
## data_chart ##

from copy import copy

class data_chart(object):
    """\brief object keeping the data of chart
    """
    color = (0, 0, 0)
    legend = ''
    def __init__(self, data_list):
        """
        \param data_list list of tuples with data (X axis data, Y axis data)
        """
        self._data_list = data_list
        
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
            assert(len(elt) == 2, 'The length of elements in data list must be 2')
        self._data_list = copy(data_list).sort()

    def append_data(self, data):
        """\brief append data to data list and resort it
        \param data tuple with data or list of tuples
        """
        if isinstance(data, tuple):
            assert(len(data) == 2, 'Length of tuple in data must be exactly 2')
            self._data_list.append(data)
        elif isinstance(data, list):
            for elt in data:
                assert(len(elt) == 2, 'The length of tuples in data must be 2')
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
        self._color = color

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

        

