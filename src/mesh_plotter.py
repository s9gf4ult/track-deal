#!/bin/env python
# -*- coding: utf-8 -*-
## mesh_plotter ##

from common_drawer import common_drawer
from od_exceptions import od_exception, od_exception_parameter_error
from cairo_rectangle import cairo_rectangle
from font_store import font_store
from common_methods import format_number, map_to_context_coordinates, months_range, years_range
from drawing_rectangle import drawing_rectangle
from datetime import datetime
from time import mktime
from math import trunc

class mesh_plotter(common_drawer, font_store):
    """\brief draw mesh and rullers
    """
    _color = (0, 0, 0)
    ## instance of \ref drawing_rectangle.drawing_rectangle
    _rectangle = None
    _chart_area_rectangle = None
    _line_width = 1
    def draw(self, context, rectangle):
        """\brief draw the mesh
        \param context - cairo context
        \param rectangle - cairo context rectangle
        """
        fextent = self.get_font_extent(context)
        if self._rectangle == None:
            raise od_exception('you must specify rectangle before drawing')
        if issubclass(self._rectangle.get_x_axis_type(), datetime):
            chartheight = rectangle.height - (2 * fextent[2]) - (4 * self._line_width) # height of the chart area
            numbers = trunc(chartheight / fextent[2]) # the max count of numbers can be displayed in vertical colon (y label)
            draw_numbers = self._generate_numbers(self._rectangle.get_lower_y_limit(), self._rectangle.get_upper_y_limit(), numbers) # generated numbers to draw
            chartwidth = rectangle.width - self._get_max_number_width(context, draw_numbers) - self._line_width * 2 # width of the chart area
            self._chart_area_rectangle = cairo_rectangle(rectangle.x, rectangle.y, chartwidth, chartheight)
            y_numbers_coordinates = self._map_y_numbers_to_context(self._chart_area_rectangle, self._rectangle, draw_numbers)
            self._draw_vertical_colon_numbers(context, rectangle.x + chartwidth + self._line_width, y_numbers_coordinates, draw_numbers)
            context.set_source_rgb(*self._color)
            context.set_line_width(self._line_width * 0.5)
            context.set_dash([3, 7])
            self._draw_horizontal_lines(context, rectangle.x, rectangle.x + chartwidth, y_numbers_coordinates) # draw dash lines in the chart area
            context.stroke()
            context.set_dash([1,0])
            # draw rectangle and two horizontal lines at bottom of the chart
            context.set_line_width(self._line_width)
            context.rectangle(rectangle.x, rectangle.y, chartwidth, rectangle.height)
            line1y = rectangle.y + chartheight
            line2y = line1y + fextent[2] + (2 * self._line_width)
            context.move_to(rectangle.x, line1y)
            context.line_to(rectangle.x + chartwidth, line1y)
            context.move_to(rectangle.x, line2y)
            context.line_to(rectangle.x + chartwidth, line2y)
            context.stroke()
            # draw dates at bottom of the chart and vertical dash lines
            (small_coords, big_coords) = self._draw_horizontal_dates(context, rectangle, line1y + self._line_width, line2y + self._line_width) # draw dates and return X coordinates of vertical lines in context coorinate system
            # draw vertical small lines
            context.set_line_width(self._line_width)
            context.set_source_rgb(self._color)
            self._draw_vertical_lines(context, line1y, line2y, small_coords)
            # draw vertical big lines
            self._draw_vertical_lines(context, line2y, rectangle.y + rectangle.height, big_coords)
            context.stroke()
            # draw vertical dashes
            context.set_source_rgb(*self._color)
            context.set_line_width(self._line_width * 0.5)
            context.set_dash([3, 7])
            self._draw_vertical_lines(context, rectangle.y, line1y, small_coords)
            context.stroke()
            
            
        else:
            raise NotImplementedError()

    def _draw_horizontal_dates(self, context, cairo_rectangle, small_y, big_y):
        """\brief draw small and big dates along X axis in coordinates small_y and big_y, mapping coorinates from lower_data_x and upper_data_x to context coordinate system
        \param context - cairo context
        \param cairo_rectangle - object with x, y, width and height fields
        \param small_y - Y coordinate of small dates line
        \param big_y - Y coordinate of big dates line
        \return two tuple of lists of small and big dates coordinates
        """
        width = cairo_rectangle.width
        lower_data_x = self._rectangle.get_lower_x_limit()
        upper_data_x = self._rectangle.get_upper_x_limit()
        max60 = self._get_60_max(context) # max width of text from 10 to 59 (to draw seconds)
        date_range = upper_data_x - lower_data_x
        date_range = date_range.seconds + (date_range.days * 24 * 60 * 60) # seconds between lower_data_x and upper_data_x
        if trunc(date_range) <= trunc(width / max60): # we can draw all seconds 
            return self._draw_horizontal_seconds(context, cairo_rectangle, small_y, big_y)
        max_time_width = self._get_max_time_width(context) # max width of time string (e.g. 12:34)
        if trunc(date_range / 60) <= trunc(width / max_time_width): # we can draw time up to minutes
            return self._draw_horizontal_minutes(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 5)) <= trunc(width / max_time_width): # we can draw time up to 5 minute ranges
            return self._draw_horizontal_five_minutes(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 10)) <= trunc(width / max_time_width):
            return self._draw_horizontal_ten_minutes(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 20)) <= trunc(width / max_time_width):
            return self._draw_horizontal_twenty_minutes(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 30)) <= trunc(width / max_time_width):
            return self._draw_horizontal_half_hour(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 60)) <= trunc(width / max_time_width):
            return self._draw_horizontal_hour(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 60 * 2)) <= trunc(width / max_time_width):
            return self._draw_horizontal_two_hours(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 60 * 3)) <= trunc(width / max_time_width):
            return self._draw_horizontal_three_hours(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 60 * 6)) <= trunc(width / max_time_width):
            return self._draw_horizontal_six_hours(context, cairo_rectangle, small_y, big_y)
        if trunc(date_range / (60 * 60 * 12)) <= trunc(width / max_time_width):
            return self._draw_horizontal_twelve_hours(context, cairo_rectangle, small_y, big_y)
        max31 = self._get_31_max(context) # height 
        if trunc(date_range / (60 * 60 * 24)) <= trunc(width / max31):
            return self._draw_horizontal_day(context, cairo_rectangle, small_y, big_y)
        max_month = self._get_month_max(context)
        if months_range(lower_data_x, upper_data_x) <= trunc(width / max_month):
            return self._draw_horizontal_month(context, cairo_rectangle, small_y, big_y)
        max12 = self._get_12_max(context)
        if months_range(lower_data_x, upper_data_x) <= trunc(width / max12):
            return self._draw_horizontal_month_digit(context, cairo_rectangle, small_y, big_y)
        if years_range(lower_data_x, upper_data_x) <= trunc(width / max12):
            return self._draw_horizontal_year(context, cairo_rectangle, small_y, big_y)
        return ([], [])

    def _draw_horizontal_seconds(self, context, cairo_rectangle, small_y, big_y):
        """\brief draw seconds in small time lint and time in big time
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        lower, upper = self._rectangle.get_lower_x_limit(), self._rectangle.get_upper_x_limit()
        seconds = self._generate_times(lower, upper, 1)
        minutes = self._generate_times(lower, upper, 60)
        sec_coords = self._map_x_numbers_to_context(cairo_rectangle, self._rectangle, seconds)
        min_coords = self._map_x_numbers_to_context(cairo_rectangle, self._rectangle, minutes)
        self._draw_horizontal_numbers(context, small_y, sec_coords, map(lambda a: a.second, seconds), cairo_rectangle.x + cairo_rectangle.width)
        self._draw_horizontal_times(context, big_y, min_coords, minutes, cairo_rectangle.x + cairo_rectangle.width)
        return (sec_coords, min_coords)

    def _draw_horizontal_minutes(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 1)

    def _draw_horizontal_five_minutes(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 5)
    
    def _draw_horizontal_ten_minutes(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 10)

    def _draw_horizontal_twenty_minutes(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 20)
    
    def _draw_horizontal_half_hour(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 30)

    def _draw_horizontal_hour(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 60)

    def _draw_horizontal_two_hours(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 120)

    def _draw_horizontal_three_hours(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 3 * 60)

    def _draw_horizontal_six_hours(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 6 * 60)

    def _draw_horizontal_twelve_hours(self, context, cairo_rectangle, small_y, big_y):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        """
        return self._draw_horizontal_multiplied_minutes(context, cairo_rectangle, small_y, big_y, 12 * 60)

    def _draw_horizontal_multiplied_minutes(self, context, cairo_rectangle, small_y, big_y, multiplier):
        """\brief 
        \param context
        \param cairo_rectangle
        \param small_y
        \param big_y
        \param multiplier - int, count of minutes per frame in small date line
        """
        lower, upper = self._rectangle.get_lower_x_limit(), self._rectangle.get_upper_x_limit()
        minutes = self._generate_times(lower, upper, 60 * multiplier)
        days = self._generate_times(lower, upper, 24 * 3600)
        min_coords = self._map_x_numbers_to_context(cairo_rectangle, self._rectangle, minutes)
        self._draw_horizontal_times(context, small_y, min_coords, minutes, cairo_rectangle.x + cairo_rectangle.width)
        if len(days) == 0:
            day_coords = []
            daystring = lower.strftime('%Y %B %d')
            context.set_source_rgb(*self._color)
            context.select_font_face(self._family, self._slant, self._weight)
            textent = context.text_extents(daystring)
            if cairo_rectangle.width > textent[2]: # if text can be placed in width
                context.move_to(cairo_rectangle.x + ((cairo_rectangle.width - textent[2]) / 2),
                                small_y)
                context.show_text(daystring)
        else:
            day_coords = self._map_x_numbers_to_context(cairo_rectangle, self._rectangle, days)
            self._draw_horizontal_days(context, big_y, day_coords, days, cairo_rectangle.x + cairo_rectangle.width)
        return (min_coords, day_coords)

    def _draw_horizontal_days(self, context, y, xx, data, max_x):
        """\brief 
        \param context
        \param y
        \param xx
        \param data - list of datetime instances
        \param max_x
        """
        self._draw_horizontal_text_elements(context, y, xx, map(lambda a: a.strftime('%Y %B %d'), data), max_x)

        
    def _generate_times(self, low_time, up_time, timeframe):
        """\brief generate list of datetime instances of timeframe multiples
        \param low_time
        \param up_time
        \param timeframe - time frame in seconds
        """
        ltime = mktime(low_time.timetuple())
        utime = mktime(up_time.timetuple())
        ret = []
        current = trunc(ltime / timeframe) * timeframe
        if current != ltime:
            current += timeframe
        while current <= utime:
            ret.append(datetime.fromtimestamp(current))
            current += timeframe
        return ret

    def _map_x_numbers_to_context(self, cairo_rectangle, data_rectangle, data):
        """\brief 
        \param cairo_rectangle - cairo rectangle 
        \param data_rectangle - \ref drawing_rectangle.drawing_rectangle instance
        \param data - X coordinates in data context
        """
        yy = data_rectangle.get_lower_y_limit() # common Y for all points to map
        mapped = map_to_context_coordinates(data_rectangle, cairo_rectangle, map(lambda a: (a, yy), data))
        return map(lambda a: a[0], mapped) # using just X
        
    def _draw_horizontal_numbers(self, context, y, xx, data, max_x):
        """\brief 
        \param context - cairo context
        \param y - Y coordinate in cairo context
        \param xx - list of floats, X coordinates in cairo context
        \param data - list of floats, numbers to draw
        \param max_x - float
        """
        self._draw_horizontal_text_elements(context, y, xx, map(lambda a: format_number(a), data), max_x)

    def _draw_horizontal_text_elements(self, context, y, xx, data, max_x):
        """\brief 
        \param context
        \param y
        \param xx
        \param data
        \param max_x
        """
        context.set_source_rgb(*self._color)
        context.select_font_face(self._family, self._slant, self._weight)
        tent = context.font_extents()
        for (x, tt) in zip(xx, data):
            tx = context.text_extents(tt)
            if not (x + tx[2] > max_x):
                context.move_to(x, y + tent[0])
                context.show_text(tt)
        
    def _draw_horizontal_times(self, context, y, xx, data, max_x):
        """\brief 
        \param context - cairo context
        \param y float 
        \param xx - list of floats
        \param data - list of datetime instances
        """
        self._draw_horizontal_text_elements(context, y, xx, map(lambda a: a.strftime('%H:%M'), data), max_x)

    def _get_60_max(self, context):
        """\brief return max width of text from 10 to 59
        \param context
        """
        return self._get_from_to_max_width(context, 10, 59)
        
    def _get_12_max(self, context):
        """\brief return max width of text from 10 to 12
        \param context
        """
        return self._get_from_to_max_width(context, 10, 12)

    def _get_31_max(self, context):
        """\brief return max width of text from 10 to 31
        \param context
        """
        return self._get_from_to_max_width(context, 10, 31)

    def _get_from_to_max_width(self, context, lower, upper):
        """\brief return max width of text of digits given in range
        \param context - cairo context
        \param from int, lower limit
        \param upto int, upper limit
        """
        context.select_font_face(self._family, self._slant, self._weight)
        return max(map(lambda a: context.text_extents(str(a))[2], xrange(lower, upper + 1))) + (2 * self._line_width)

    def _get_month_max(self, context):
        """\brief return max width of all posible names of month
        \param context
        """
        monthnames  = map(lambda a: unicode(datetime(2000, a, 1).strftime('%B')), xrange(1, 13)) # names of the month
        context.select_font_face(self._family, self._slant, self._weight)
        return max(map(lambda a: context.text_extents(a)[2], monthnames)) + (2 * self._line_width)
        
    def _get_max_time_width(self, context):
        """\brief return width of text explaining time
        \param context
        """
        context.select_font_face(self._family, self._slant, self._weight)
        return context.text_extents('23:59')[2] + (2 * self._line_width) # FIXME this is not precisely way

    def _draw_vertical_lines(self, context, y1, y2, xx):
        """\brief draw vertical lines from (xx[0], y1) to (xx[0], y2) and so on for every element in xx
        \param context - cairo context
        \param y1 - top Y coordinate
        \param y2 - bottom Y coordinate
        \param xx - list of X coordinates
        """
        for xc in xx:
            context.move_to(xc, y1)
            context.line_to(xc, y2)

    def _generate_numbers(self, low_limit, up_limit, maxnumbers):
        """\brief generate list of number can be drawed between limits
        \param low_limit - float, lower limit of the range
        \param up_limit - float, upper limit
        \param maxnumbers - int, maximum count of numbers can be drawed
        """
        if maxnumbers < 0:
            raise od_exception_parameter_error(u'maxnumbers must at least 0')
        elif maxnumbers == 0:
            return []
        rng = trunc(up_limit - low_limit)
        if rng > maxnumbers:
            multiplier = self._find_ascending_multiplier(low_limit, up_limit, maxnumbers)
        elif rng < maxnumbers:
            multiplier = self._find_descending_multiplier(low_limit, up_limit, maxnumbers)
        else:
            multiplier = 1
        first = (low_limit if low_limit % multiplier == 0 else (trunc(low_limit / multiplier) + 1) * multiplier) # first drawing number
        ret = []
        while first <= up_limit:
            ret.append(first)
            first += multiplier
        return ret

    def _find_descending_multiplier(self, low_limit, up_limit, maxnumbers):
        """\brief return multiplier less than 1
        \param low_limit - low limit of the range
        \param up_limit - up limit of the range
        \param maxnumbers - int, maximum numbers
        """
        rng = up_limit - low_limit
        mlt = 1
        while True:
            if trunc(rng / (mlt * 0.5)) > maxnumbers:
                return mlt
            if trunc(rng / (mlt * 0.2)) > maxnumbers:
                return mlt * 0.5
            if trunc(rng / (mlt * 0.1)) > maxnumbers:
                return mlt * 0.2
            mlt /= 10.

    def _find_ascending_multiplier(self, low_limit, up_limit, maxnumbers):
        """\brief return multiplier more then 1
        \param low_limit - low limit of the range
        \param up_limit - up limit of the range
        \param maxnumbers - int, maximum numbers
        """
        rng = up_limit - low_limit
        mlt = 1
        while True:
            if trunc(rng / (mlt * 2)) <= maxnumbers:
                return mlt * 2
            if trunc(rng / (mlt * 5)) <= maxnumbers:
                return mlt * 5
            if trunc(rng / (mlt * 10)) <= maxnumbers:
                return mlt * 10
            mlt *= 10

    def _map_y_numbers_to_context(self, cairo_rect, data_rect, y_numbers):
        """\brief 
        \param cairo_rect - rectangle of cairo context
        \param data_rect - rectangle of data
        \param y_numbers - list of numbers
        \return list of floats, y coordinates in cairo context
        """
        xx = data_rect.get_upper_x_limit()
        maped = map_to_context_coordinates(data_rect, cairo_rect, map(lambda a: (xx, a), y_numbers))
        return map(lambda a: a[1], maped) # we do not use X - it is always 0

    def _draw_vertical_colon_numbers(self, context, left_x, y_coordinates, numbers):
        """\brief 
        \param context - cairo context
        \param left_x - X coordinate of left top corner of colon
        \param y_coordinates - coordinates of the middle of each text
        \param numbers - list of numbers, numbers to draw
        """
        if len(y_coordinates) != len(numbers):
            raise od_exception_parameter_error(u'length of y_coordinates and numbers parameters must be same')
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        context.set_source_rgb(*self._color)
        fextent = context.font_extents()
        for y_cord, nmb in zip(y_coordinates, numbers):
            context.move_to(left_x, y_cord - (fextent[2] / 2.) + fextent[0])
            context.show_text(format_number(nmb, 6))

    def _draw_horizontal_lines(self, context, left_x, right_x, y_coordinates):
        """\brief 
        \param context
        \param left_x
        \param right_x
        \param y_coordinates
        """
        for yy in y_coordinates:
            context.move_to(left_x, yy)
            context.line_to(right_x, yy)

    def _get_max_number_width(self, context, numbers):
        """\brief return width of numbers colon
        \param context - cairo context
        \param numbers - list of numbers, number values to calculate maximum width of
        """
        context.select_font_face(self._family, self._slant, self._weight)
        context.set_font_size(self._size)
        return max(map(lambda a: context.text_extents(format_number(a, max_after_comma = 6))[2], numbers))
        
    def set_line_width(self, line_width):
        """\brief Setter for property line_width
        \param line_width
        """
        self._line_width = line_width

    def get_line_width(self):
        """\brief Getter for property line_width
        """
        return self._line_width

    def set_color(self, color):
        """\brief Setter for property color
        \param color - tuple of three floats
        """
        self._color = color

    def set_rectangle(self, rectangle):
        """\brief Setter for property rectangle
        \param rectangle - \ref drawing_rectangle.drawing_rectangle instance
        """
        self._rectangle = rectangle
        
    def get_chart_area_rectangle(self, ):
        """\brief return rectangle of the chart area in cairo context
        """
        if self._chart_area_rectangle == None:
            raise od_exception('you must call draw, then get chart area rectangle')
        return self._chart_area_rectangle
