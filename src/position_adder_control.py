#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
import sys
from common_methods import *
from hide_control import hide_control
from datetime_start_end_control import *
from datetime_control import *
from time_control import *
from number_range_control import *
from combo_select_control import combo_select_control
from select_control import *

class position_adder_control:
    def __init__(self, parent):
        self._parent = parent
        self.builder = make_builder('glade/padder.glade')
        def shorter(name):
            return self.builder.get_object(name)
        w = shorter("padder")
        w.set_transient_for(self._parent.window.builder.get_object('main_window'))
        w.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.hiders = [hide_control(shorter("padder_calendars"), [shorter("padder_lower_calendar"), shorter("padder_upper_calendar")], hide = True)]
        self.start_date = datetime_control(shorter("padder_lower_calendar"),
                                           time_control(*map(lambda a: shorter(u'padder_lower_{0}'.format(a)), ["hour", "min", "sec"])),
                                           year = shorter("padder_lower_year"),
                                           month = shorter("padder_lower_month"),
                                           day = shorter("padder_lower_day"))
        
        self.end_date = datetime_control(shorter("padder_upper_calendar"),
                                         time_control(*map(lambda a: shorter(u'padder_upper_{0}'.format(a)), ["hour", "min", "sec"])),
                                         year = shorter("padder_upper_year"),
                                         month = shorter("padder_upper_month"),
                                         day = shorter("padder_upper_day"))
                                           
        self.datetime_start_end = datetime_start_end_control(self.start_date, self.end_date)
        self.price = number_range_control(number_control(shorter("padder_open"), step_incr = 0.1, digits = 4),
                                          number_control(shorter("padder_close"), step_incr = 0.1, digits = 4))
        self.price.set_lower_limit(0)
        self.price.set_upper_limit(sys.float_info.max)

        self.commission = number_range_control(number_control(shorter("padder_open_comm"), step_incr = 0.1, digits = 4),
                                               number_control(shorter("padder_close_comm"), step_incr = 0.1, digits = 4))
        self.commission.set_lower_limit(0)
        self.commission.set_upper_limit(sys.float_info.max)

        self.instrument = combo_select_control(shorter("padder_instrument"))
        self.account = combo_select_control(shorter('padder_account'))
        self.long_short = select_control({-1 : shorter("padder_long"),
                                          1 : shorter("padder_short")})
        self.count =  number_control(shorter("padder_count"))
        self.count.set_lower_limit(0)
        self.count.set_upper_limit(sys.maxint)

    def get_data(self, ):
        """\brief return data to insert into model
        """
        return {'account_id' : self.account.get_value(),
                'paper_id' : self.instrument.get_value(),
                'count' : self.count.get_value(),
                'direction' : self.long_short.get_value(),
                'open_commission' : self.commission.get_lower_value(),
                'close_commission' : self.commission.get_upper_value(),
                'open_datetime' : self.start_date.get_datetime(),
                'close_datetime' : self.end_date.get_datetime(),
                'open_points' : self.price.get_lower_value(),
                'close_points' : self.price.get_upper_value(),
                'manual_made' : 1}

    def update_widget(self, ):
        """\brief update comboboxes
        """
        if not self._parent.connected():
            return
        self.update_accounts()
        self.update_instruments()
        
    def update_accounts(self, ):
        """\brief update accounts box
        """
        accs = self._parent.model.list_accounts(['name'])
        self.account.update_answers(map(lambda a: (a['id'], a['name']), accs))
        got = self.account.get_value()
        if is_null_or_empty(got):
            cacc = self._parent.model.get_current_account()
            if cacc <> None:
                self.account.set_value(cacc['id'])
                
    def update_instruments(self, ):
        """\brief update instruments box
        """
        insts = self._parent.model.list_papers(['name'])
        self.instrument.update_answers(map(lambda a: (a['id'], a['name']), insts))

    def run(self):
        """\brief run dialog and return result
        \retval gtk.RESPONSE_ACCEPT
        \retval gtk.RESPONSE_CANCEL
        """
        w = self.builder.get_object("padder")
        self.start_date.set_current_datetime()
        self.end_date.set_current_datetime()
        w.show_all()
        ret = w.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if self.check_correctness():
                break
            else:
                ret = w.run()
        w.hide()
        return ret

    def check_correctness(self):
        errs = []
        if not self.price.get_lower_value() > 0:
            errs.append(u'Необходимо указать цену открытия')
        if not self.price.get_upper_value() > 0:
            errs.append(u'Необходимо указать цену закрытия')
        if is_null_or_empty(self.instrument.get_value()):
            errs.append(u'Необходимо выбрать инструмент')
        if is_null_or_empty(self.account.get_value()):
            errs.append(u'Необходимо выбрать класс инструмента')
        if not self.count.get_value() > 0:
            errs.append(u'Неоходимо указать количество бумаг в позиции')
        if len(errs) > 0:
            show_error(reduce(lambda a, b:u'{0}\n{1}'.format(a, b),
                              errs),
                       self.builder.get_object("padder"))
            return False
        else:
            return True
            
            
if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = position_adder_control(b)
    con.run()
