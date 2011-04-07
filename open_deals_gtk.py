#!/bin/env python
# -*- coding: utf-8 -*-
import sources
import deals_core
import gtk
import sqlite3
import datetime
import re
import traceback
from deals_filter import deals_filter
from deal_adder_control import deal_adder_control
from deals_tab_controller import deals_tab_controller
from report_tab_control import report_tab_control
from blog_text_tab_controller import blog_text_tab_controller

class main_ui():
    def _stock_cursor_changed(self, tw):
        path = tw.get_cursor()[0]
        stock_store = self.builder.get_object("stock_store")
        date_store = self.builder.get_object("date_store")
        stock = stock_store.get_value(stock_store.get_iter(path), 0)
        
        ii = date_store.get_iter_first()
        while ii:
            date_store.remove(ii)
            ii = date_store.get_iter_first()
            
        for (pid, pcount, bdate, edate) in self.database.connection.execute("select id, count, open_datetime, close_datetime from positions where ticket = ? order by close_datetime, open_datetime, count", (stock,)):
            ins = map(lambda a: a.isoformat(), [bdate, edate])
            date_store.append(ins + [pcount, pid])

    def _get_text_for_blog(self, pid):
        (ticket, direction, open_date, close_date, open_coast, close_coast, count, com, pl_net) = self.database.connection.execute("select ticket, direction, open_datetime, close_datetime, open_coast, close_coast, count, broker_comm + stock_comm, pl_net from positions where id = ?", (pid,)).fetchone()
        isprof = pl_net > 0
        ret = u'''{0} {1} позиция по {2} инструмента {3}.
Цена открытия {4} в {5}.
Цена закрытия {6} в {7}.
Движение составило {8}.
{9}.
{10}
'''.format(direction == -1 and u'Длинная' or u'Короткая',
           pl_net > 0 and u'прибыльная' or u'убыточная',
           count == 1 and u'1 контракту' or u'{0} контрактам'.format(count),
           ticket,
           open_coast, open_date.isoformat(),
           close_coast, close_date.isoformat(),
           abs(open_coast - close_coast),
           pl_net > 0 and u'Прибыль составила {0}'.format(pl_net) or u'Убыток составил {0}'.format(-pl_net),
           com > 0 and u'Комиссия составила {0}.\n'.format(com) or '')
        return ret

    def _date_cursor_changed(self, tw):
        path = tw.get_cursor()[0]
        date_store = self.builder.get_object("date_store")
        blog_buffer = self.builder.get_object("blog_buffer")
        pid = date_store.get_value(date_store.get_iter(path), 3)
        blog_buffer.set_text(self._get_text_for_blog(pid))
        

    def quit(self, wid):
        try:
            self.database.close()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())
            return True
        gtk.main_quit()
        return False

    def window_quit(self, wid, evt):
        return self.quit(wid)
        
    def create_in_memory(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection:
            self.database.create_new(":memory:")
            self.update_view()

    def create_in_file(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection:
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Новая база', parent = win, action = gtk.FILE_CHOOSER_ACTION_SAVE)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self.database.create_new(diag.get_filename())
                    self.update_view()
                except Exception as e:
                    self.show_error(e.__str__())
                    print(traceback.format_exc())
            diag.destroy()

    def open_existing(self, wid):
        if self.database.connection:
            self.close(None)
        if not self.database.connection: # это значит если база закрылась
            win = self.builder.get_object("main_window")
            diag = gtk.FileChooserDialog(title = u'Открыть базу', parent = win, action = gtk.FILE_CHOOSER_ACTION_OPEN)
            diag.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            diag.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
            fl = gtk.FileFilter()
            fl.add_mime_type('application/x-sqlite3')
            diag.set_filter(fl)
            if diag.run() == gtk.RESPONSE_ACCEPT:
                try:
                    self.database.open_existing(diag.get_filename())
                    self.update_view()
                except Exception as e:
                    self.show_error(e.__str__())
                    print(traceback.format_exc())
            diag.destroy()
            fl.destroy()
            
    def close(self, wid):
        try:
            self.database.close()
            self.update_view()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())

    def commit(self, wid):
        if self.database.connection:
            self.database.commit()

    def rollback(self, wid):
        if self.database.connection:
            self.database.rollback()
            self.update_view()


    def check_if_database_open(self):
        if self.database.connection:
            return True
        else:
            self.show_error(u'Необходимо открыть или создать новую базу данных')
            return False

    def make_positions(self, wid):
        if self.check_if_database_open():
            self.database.make_positions()
            self.update_view()

    def __init__(self):
        self.database = deals_core.deals_proc()
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        self.builder.connect_signals({"on_main_window_delete_event" : self.window_quit,
                                      "on_create_database_in_memory_activate" : self.create_in_memory,
                                      "on_create_database_activate" : self.create_in_file,
                                      "on_open_database_activate" : self.open_existing,
                                      "on_close_database_activate" : self.close,
                                      "on_transaction_commit_activate" : self.commit,
                                      "on_transaction_rollback_activate" : self.rollback,
                                      "on_positions_make_activate" : self.make_positions,
                                      "on_quit_activate" : self.quit})

        # report tab
        self.report_tab = report_tab_control(self.database, self.builder)

        # blog tab
        self.blog_tab = blog_text_tab_controller(self.database, self.builder)

        # deals tab
        self.deals_filter = deals_filter(self.builder, self.database)
        self.deal_adder = deal_adder_control(self.builder)
        self.deals_tab = deals_tab_controller(self.database, self.builder, self.update_view, self.deals_filter, self.deal_adder)
        
    def show_error(self, text):
        win = self.builder.get_object("main_window")
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
        dial.props.text = text
        dial.run()
        dial.destroy()
        
    def _flush_store(self, store):
        it = store.get_iter_first()
        while it:
            store.remove(it)
            it = store.get_iter_first()

    def update_blog_tab(self):
        date_store = self.builder.get_object("date_store")
        stock_store = self.builder.get_object("stock_store")
        for store in [date_store, stock_store]:
            self._flush_store(store)
        self.builder.get_object("blog_buffer").set_text("")
        if not self.database.connection:
            return
        for (ticket,) in self.database.connection.execute("select distinct ticket from positions order by ticket"):
            stock_store.append([ticket])

    def update_view(self):
        self.deals_tab.update_widget()
        self.report_tab.update_widget()
        self.blog_tab.update_widget()

    def show(self):
        win = self.builder.get_object("main_window")
        win.show_all()

        
if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
