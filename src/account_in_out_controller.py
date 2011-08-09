#!/bin/env python
# -*- coding: utf-8 -*-
## account_in_out_controller ##

from common_methods import make_builder
from list_view_sort_control import list_view_sort_control
from time_control import time_control
from datetime_control import datetime_control

class account_in_out_controller(object):
    """\brief entry withdrawall from the account dialog controller
    """
    def __init__(self, parent):
        """\brief 
        \param parent
        """
        self._parent = parent
        self.builder = make_builder('glade/account_in_out.glade')
        def shobject(name):
            return self.builder.get_object(name)

        self.list = list_view_sort_control(shobject('in_out_list'), [['id', int], (u'Счет', str), (u'Дата', str), (u'Деньги', str)])
        self.account = shobject('account')
        time = time_control(shobject('hour'), shobject('minute'), shobject('second'))
        self.datetime = datetime_control(shobject('calendar'), time, year = shobject('year'), month = shobject('month'), day = shobject('day'))
        self.amount = shobject('amount')
        shobject('add').connect('clicked', self.add_clicked)
        shobject('delete').connect('clicked', self.delete_clicked)
        shobject('modify').connect('clicked', self.modify_clicked)

    def add_clicked(self, button):
        """\brief 
        \param button
        """
        pass

    def delete_clicked(self, button):
        """\brief 
        \param button
        """
        pass

    def modify_clicked(self, button):
        """\brief 
        \param button
        """
        pass



                                                  
