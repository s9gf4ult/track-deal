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

    def radio_report_toggled(self, wid):
        if wid.get_active():
            self.update_report_buffer()

    def _call_filter_clicked(self, bt):
        if not self.database.connection:
            return
        self.deals_filter.run()
        self.update_deals_tab()

    def _update_deals_activated(self, action):
        self.update_deals_tab()

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
                                      # "on_deals_load_open_ru_activate" : self.load_open_ru,
                                      "on_positions_make_activate" : self.make_positions,
                                      "on_radio_segfault_toggled" : self.radio_report_toggled,
                                      "on_radio_axce1_toggled" : self.radio_report_toggled,
                                      "on_comma_as_splitter_toggled" : self.update_report,
                                      "on_comma_separator_value_changed" : self.update_report,
                                      "on_stock_view_cursor_changed" : self._stock_cursor_changed,
                                      "on_date_view_cursor_changed" : self._date_cursor_changed,
                                      # "on_call_deals_filter_clicked" : self._call_filter_clicked,
                                      # "on_update_deals_tab_activate" : self._update_deals_activated,
                                      # "on_delete_deals_activate" : self.delete_deals_activate,
                                      # "on_add_deal_activate" : self.add_deal_activate,
                                      "on_quit_activate" : self.quit})

        # report tab
        self.report_tab = report_tab_control(self.database, self.builder)

        # blog tab
        stock_view = self.builder.get_object("stock_view")
        date_view = self.builder.get_object("date_view")
        stock_view.append_column(gtk.TreeViewColumn(u'Сток',gtk.CellRendererText(), text = 0))
        date_view.append_column(gtk.TreeViewColumn(u'Дата открытия', gtk.CellRendererText(), text = 0))
        date_view.append_column(gtk.TreeViewColumn(u'Дата закрытия', gtk.CellRendererText(), text = 1))
        date_view.append_column(gtk.TreeViewColumn(u'Количество', gtk.CellRendererText(), text = 2))

        # deals tab
        self.deals_filter = deals_filter(self.builder, self.database)
        self.deal_adder = deal_adder_control(self.builder)
        self.deals_tab = deals_tab_controller(self.database, self.builder, self.update_view, self.deals_filter, self.deal_adder)
        
    def _gen_seg(self, ticks):
        ret = u''
        is_comma = self.builder.get_object("comma_as_splitter").get_active()
        after_comma = self.builder.get_object("comma_separator").get_value_as_int()
        for pos in self.database.connection.execute("select ticket, direction, count, open_coast, close_coast, broker_comm + stock_comm, open_datetime, close_datetime from positions order by close_datetime, open_datetime"):
            if not pos[0] in ticks:
                continue
            (open_datetime, close_datetime) = map(lambda a: u'{0:4}.{1:02}.{2:02}'.format(a.year, a.month, a.day), pos[-2:])
            ret += u'{0}\t{1}'.format(pos[0], -1 == pos[1] and 'L' or 'S')
            v = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: after_comma < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, after_comma), pos[2:-2]))
            if is_comma:
                v = v.replace('.', ',')
            ret += u'\t{0}\t\t\t\t\t\t{1}\t{2}\n'.format(v, open_datetime, close_datetime)
        return ret

    def _gen_axcel(self, ticks):
        after_comma = self.builder.get_object("comma_separator").get_value_as_int()
        is_comma = self.builder.get_object("comma_as_splitter").get_active()
        ret = u''
        for pos in self.database.connection.execute("select open_datetime, close_datetime, ticket, direction, open_coast, close_coast, count, open_volume, close_volume, broker_comm + stock_comm from positions order by close_datetime, open_datetime"):
            if not pos[2] in ticks:
                continue
            vvv = map(lambda a: [u'{0:02}.{1:02}.{2:04}'.format(a.day, a.month, a.year), u'{0:02}:{1:02}:{2:02}'.format(a.hour, a.minute, a.second)], pos[:2])
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), vvv[0] + vvv[1])
            ret += u'\t{0}\t{1}'.format(pos[2], -1 == pos[3] and 'L' or 'S')
            aa = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: after_comma < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, after_comma), pos[4:-1]))
            aa += u'\t\t\t\t{0}'.format(after_comma < 1 and u'{0}'.format(float(pos[-1]).__trunc__()) or u'{0}'.format(round(pos[-1], after_comma)))
            if is_comma:
                aa = aa.replace('.', ',')
            ret += u'\t{0}\n'.format(aa)
            
        return ret

    def show_error(self, text):
        win = self.builder.get_object("main_window")
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = win)
        dial.props.text = text
        dial.run()
        dial.destroy()
        
    def update_report(self, tb):
        self.update_report_buffer()

    def _flush_store(self, store):
        it = store.get_iter_first()
        while it:
            store.remove(it)
            it = store.get_iter_first()

    def update_report_tab(self):
        self.update_report_buttons()
        self.update_report_buffer()
    
    def update_report_buffer(self):
        buf = self.builder.get_object("buffer") # буфер отчета
        if not self.database.connection:
            buf.set_text("")
            return
        
        pack = self.builder.get_object("stock_buttons")
        ticks = []
        pack.foreach(lambda w: w.__class__ == gtk.ToggleButton and w.get_active() and ticks.append(w.get_label()))
        if self.builder.get_object("radio_segfault").get_active():
            buf.set_text(self._gen_seg(ticks))
        elif self.builder.get_object("radio_axce1").get_active():
            buf.set_text(self._gen_axcel(ticks))

    def update_report_buttons(self):
        stock_pack = self.builder.get_object("stock_buttons")
        stock_pack.foreach(stock_pack.remove)
        if not self.database.connection:
            return
        for (ticket,) in self.database.connection.execute("select distinct security_name from deals where not_actual is null and position_id is not null order by security_name"):
            b = gtk.ToggleButton(label = ticket)
            b.set_active(True)
            b.connect("toggled", self.update_report)
            stock_pack.pack_start(b, False, True, 5)
        resall = gtk.Button(u'Сбросить все')
        resall.connect("clicked", lambda ww: stock_pack.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(False)))
        stock_pack.pack_end(resall, False, True)
        invall = gtk.Button(u'Реверс все')
        invall.connect("clicked", lambda ww: stock_pack.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(not wid.get_active())))
        stock_pack.pack_end(invall, False, True)
        self.show()
        
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
        self.update_blog_tab()

    def show(self):
        win = self.builder.get_object("main_window")
        win.show_all()

        
if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
