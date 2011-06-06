#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from combo_select_control import combo_select_control
from common_methods import *

class report_importer_control:
    def __init__(self, builder):
        self.builder = builder
        w = self.builder.get_object("report_importer")
        w.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.file = self.builder.get_object("report_importer_file")
        self.report_type = self.builder.get_object("report_importer_type")
        self.account_widget = self.builder.get_object("report_importer_account")
        self.report = combo_select_control(self.report_type)
        self.account = combo_select_control(self.account_widget)

    def update_widget(self, accounts = None, report_types = None):
        if accounts != None and len(accounts) > 0:
            self.account.update_widget(accounts, none_answer = -1)
        if report_types != None and len(report_types) > 0:
            self.report.update_widget(report_types)
            if len(report_types) > 0:
                self.report.set_value(report_types[0][0])
        self.file.unselect_all()

    def get_file_name(self):
        return self.file.get_filename()

    def get_report_type(self):
        return self.report.get_value()

    def get_account_id(self):
        return self.account.get_value()

    def run(self):
        w = self.builder.get_object("report_importer")
        w.show_all()
        ret = w.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if self.check_correctness():
                w.hide()
                return True
            ret = w.run()
        w.hide()
        return None

    def check_correctness(self):
        errs = []
        if self.get_file_name() == None:
            errs.append(u'Нужно указать имя файла для загрузки')
        if self.get_report_type() == None:
            errs.append(u'Нужно указать тип файла для загрузки')

        if len(errs) > 0:
            sh = reduce(lambda a, b: u'{0}\n{1}'.format(a, b), errs)
            show_error(sh, self.builder.get_object("report_importer"))
            return False
        return True
            

if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = report_importer_control(b)
    con.update_widget([(0, "ak1"), (1, "ak2")], [(0, "type1"), (1, "type2")])
    con.run()
