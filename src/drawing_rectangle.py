#!/bin/env python
# -*- coding: utf-8 -*-
## drawing_rectangle ##

from datetime import datetime
import sys, traceback
from common_methods import is_null_or_empty
#from data_chart import data_chart

class drawing_rectangle(object):
    """\brief describes rectangle of drawing area
    """
    def __init__(self, x_axis_type = float,
                 y_axis_type = float,
                 lower_x_limit = 0,
                 upper_x_limit = 1,
                 lower_y_limit = 0,
                 upper_y_limit = 1):
        """
        \param x_axis_type - type of x axis to draw
        \param y_axis_type - type of y axis to draw
        \param lower_x_limit - the lower value of the x axis of rectangle
        \param upper_x_limit - the upper value of the x axis of rectangle
        \param lower_y_limit - the lower value of the y axis of rectangle
        \param upper_y_limit - the upper value of the y axis of rectangle
        """
        self._x_axis_type = x_axis_type
        self._y_axis_type = y_axis_type
        self._lower_x_limit = float(lower_x_limit)
        self._upper_x_limit = float(upper_x_limit)
        self._lower_y_limit = float(lower_y_limit)
        self._upper_y_limit = float(upper_y_limit)

    def get_x_axis_type(self):
        """\brief Getter for property x_axis_type
        """
        return self._x_axis_type

    def get_y_axis_type(self):
        """\brief Getter for property y_axis_type
        """
        return self._y_axis_type
    
    def set_lower_x_limit(self, lower_x_limit):
        """\brief Setter for property lower_x_limit
        \param lower_x_limit
        """
        self._lower_x_limit = float(lower_x_limit)

    def set_upper_x_limit(self, upper_x_limit):
        """\brief Setter for property upper_x_limit
        \param upper_x_limit
        """
        self._upper_x_limit = float(upper_x_limit)

    def set_lower_y_limit(self, lower_y_limit):
        """\brief Setter for property lower_y_limit
        \param lower_y_limit
        """
        self._lower_y_limit = float(lower_y_limit)

    def set_upper_y_limit(self, upper_y_limit):
        """\brief Setter for property upper_y_limit
        \param upper_y_limit
        """
        self._upper_y_limit = float(upper_y_limit)
        
    def get_lower_x_limit(self):
        """\brief Getter for property lower_x_limit
        """
        return self._lower_x_limit

    def get_upper_x_limit(self):
        """\brief Getter for property upper_x_limit
        """
        return self._upper_x_limit

    def get_lower_y_limit(self):
        """\brief Getter for property lower_y_limit
        """
        return self._lower_y_limit

    def get_upper_y_limit(self):
        """\brief Getter for property upper_y_limit
        """
        return self._upper_y_limit
    
    def shift(self, x_shift):
        """\brief shifts the region along the x axis
        \param x_shift
        """
        oldx = self.get_lower_x_limit()
        oldxx = self.get_upper_x_limit()
        try:
            self.set_lower_x_limit(self.get_lower_x_limit() + x_shift)
            self.set_upper_x_limit(self.get_upper_x_limit() + x_shift)
        except Exception as e:
            sys.stderr.write(traceback.format_exc())
            self.set_lower_x_limit(oldx)
            self.set_upper_x_limit(oldxx)
            raise e

    def autoset_y_min_max(self, data_charts):
        """\brief automatically set lower_y_limit and upper_y_limit for printing the data
        \param data_charts - the list of \ref data_chart.data_chart instances
        \note if length of data_charts is 0 then do nothing
        """
        if is_null_or_empty(data_charts):
            return
        lower = 0
        upper = 1
        for chart in data_charts:
            y = map(lambda a: a[1], chart.get_data_list())
            lower = min(lower, min(y))
            upper = max(upper, max(y))

        self.set_lower_y_limit(lower)
        self.set_upper_y_limit(upper)

    def autoset_x_min_max(self, data_charts):
        """\brief automatically set lower_x_limit and upper_x_limit to display data from data_charts
        \param data_charts - list of \ref data_chart.data_chart instances
        """
        if is_null_or_empty(data_charts):
            return
        lower, upper = 0, 1
        for chart in data_charts:
            x = map(lambda a: a[0], chart.get_data_list())
            lower = min(lower, min(x))
            upper = max(upper, max(x))

        self.set_lower_x_limit(lower)
        self.set_upper_x_limit(upper)

    def autoset_rectangle(self, data_charts):
        """\brief automatically set all rectangle attributes
        \param data_charts - list of \ref data_chart.data_chart instances
        """
        if is_null_or_empty(data_charts):
            return
        x_lower = 0
        x_upper = 0
        y_lower = 0
        y_upper = 0
        for data in data_charts:
            rect = data.get_drawing_rectangle()
            x_lower = min(x_lower, rect[0])
            x_upper = max(x_upper, rect[1])
            y_lower = min(y_lower, rect[2])
            y_upper = max(y_upper, rect[3])

        self.set_lower_x_limit(x_lower)
        self.set_upper_x_limit(x_upper)
        self.set_lower_y_limit(y_lower)
        self.set_upper_y_limit(y_upper)
        
    def shrink_chart(self, chart):
        """\brief return shrinked data
        \param chart \ref data_chart.data_chart instance
        """
        return filter(lambda a: self.get_lower_x_limit() <= a[0] <= self.get_upper_x_limit, chart.get_data_list())
