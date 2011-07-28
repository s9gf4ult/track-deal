#!/bin/env python
# -*- coding: utf-8 -*-

import gtk
from combo_select_control import combo_select_control
from common_methods import *
from combo_control import combo_control
import sources

class report_importer_control:
    def __init__(self, parent):
        self._parent = parent
        self.builder = make_builder('glade/report_importer.glade')
        w = self.builder.get_object("report_importer")
        w.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        w.set_transient_for(self._parent.window.builder.get_object('main_window'))
        self.file = self.builder.get_object("report_importer_file")
        self.report_type = self.builder.get_object("report_importer_type")
        self.account_widget = self.builder.get_object("report_importer_account")
        self.report = combo_control(self.report_type)
        self.account = combo_select_control(self.account_widget)

    def update_importer(self, ):
        if not self._parent.connected():
            return
        self.account.update_answers(map(lambda a: (a['id'], a['name']), self._parent.model.list_accounts(['name'])))
        cacc = self._parent.model.get_current_account()
        if cacc <> None:
            self.account.set_value(cacc['id'])

        names = sources.classes.keys()
        names.sort()
        self.report.update_widget(names)

    def get_file_name(self):
        return self.file.get_filename()

    def get_report_type(self):
        return gethash(sources.classes, unicode(self.report.get_value()))

    def get_account_id(self):
        return self.account.get_value()

    def run(self):
        """
        \retval gtk.RESPONSE_ACCEPT if pressed save
        \retval gtk.RESPONSE_CANCEL if pressed cancel
        """
        w = self.builder.get_object("report_importer")
        w.show_all()
        ret = w.run()
        while ret == gtk.RESPONSE_ACCEPT:
            if self.check_correctness():
                self.proceed_load()
                break
            ret = w.run()
        w.hide()
        return ret

    def proceed_load(self, ):
        """\brief load data from the report
        """
        name = self.get_file_name()
        report = self.get_report_type()
        acc_id = self.get_account_id()
        source = report()
        source.open(name)
        self._parent.model.load_from_source(acc_id, source)


    def check_correctness(self):
        errs = []
        if self.get_file_name() == None:
            errs.append(u'Нужно указать имя файла для загрузки')
        if self.get_report_type() == None:
            errs.append(u'Нужно указать тип файла для загрузки')
        if self.get_account_id() == None:
            errs.append(u'Нужно указать счет для загрузки')
        if len(errs) > 0:
            sh = reduce(lambda a, b: u'{0}\n{1}'.format(a, b), errs)
            show_error(sh, self.builder.get_object("report_importer"))
            return False
        return True
            

if __name__ == "__main__":
    b = gtk.Builder()
    b.add_from_file('main_ui.glade')
    con = report_importer_control(b)
    con.update_importer([(0, "ak1"), (1, "ak2")], [(0, "type1"), (1, "type2")])
    con.run()
