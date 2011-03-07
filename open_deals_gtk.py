#!/bin/env python
# -*- coding: utf-8 -*-
import sources
import deals_core
import gtk
import sqlite3
import datetime
import re
import traceback

class main_ui():
    def _stock_cursor_changed(self, tw, date_store):
        path = tw.get_cursor()[0]
        stock = self.stock_store.get_value(self.stock_store.get_iter(path), 0)
        ii = date_store.get_iter_first()
        while ii:
            date_store.remove(ii)
            ii = date_store.get_iter_first()
        for (pid, pcount, bdate, edate) in self.deals.connection.execute("select id, count, open_datetime, close_datetime from positions where ticket = ? order by close_datetime, open_datetime", (stock.decode('utf-8'),)):
            ins = u'{0} - {1}'.format(bdate.isoformat(), edate.isoformat())
            date_store.append([ins, pcount, pid])

    def _get_text_for_blog(self, pid):
        (ticket, direction, open_date, close_date, open_coast, close_coast, count, com, pl_net) = self.deals.connection.execute("select ticket, direction, open_datetime, close_datetime, open_coast, close_coast, count, broker_comm + stock_comm, pl_net from positions where id = ?", (pid,)).fetchone()
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
        pid = self.date_store.get_value(self.date_store.get_iter(path), 2)
        self.blog_buffer.set_text(self._get_text_for_blog(pid))

    def quit(self, wid):
        try:
            self.database.close()
            gtk.main_quit()
        except Exception as e:
            self.show_error(e.__str__())
            print(traceback.format_exc())
        
    def create_in_memory(self, wid):
        self.database.create_new(":memory:")
    
    def __init__(self):
        self.database = deals_core.deals_proc()
        self.builder = gtk.Builder()
        self.builder.add_from_file("main_ui.glade")
        self.builder.connect_signals({"on_main_window_destroy" : self.quit,
                                      "on_quit_activate" : self.quit})
        
        # self.window = a.get_object("main_window")
        # self.axce1 = a.get_object("gen_axcel")
        # self.segfault = a.get_object("gen_seg")
        # self.choose_file = a.get_object("choose_file")
        # self.buffer = a.get_object("buffer")
        # self.comma = a.get_object("comma_separator")
        # self.comma.configure(gtk.Adjustment(value=2, lower=0, upper=8, step_incr=1), 1, 0)
        # self.comma_as_splitter = a.get_object("comma_as_splitter")
        # self.stock_buttons = a.get_object("stock_buttons")
        # self.stock_store = a.get_object("stock_store")
        # self.date_store = a.get_object("date_store")
        # self.stock_view = a.get_object("stock_view")
        # self.stock_view.connect("cursor-changed", self._stock_cursor_changed, self.date_store)
        # self.date_view = a.get_object("date_view")
        # self.date_view.connect("cursor-changed", self._date_cursor_changed)
        # self.stock_view.append_column(gtk.TreeViewColumn(u'Сток',gtk.CellRendererText(), text = 0))
        # self.date_view.append_column(gtk.TreeViewColumn(u'Даты начала - конца', gtk.CellRendererText(), text = 0))
        # self.date_view.append_column(gtk.TreeViewColumn(u'Количество', gtk.CellRendererText(), text = 1))
        # self.blog_buffer = a.get_object("blog_buffer")
        # self.filefilter = a.get_object("filefilter")
        # self.filefilter.add_mime_type("application/xml")
        # self.window.connect("destroy", gtk.main_quit)
        # self.choose_file.connect("file-set", self.file_set)
        # self.segfault.connect("clicked", self.clicked, self._gen_seg)
        # self.axce1.connect("clicked", self.clicked, self._gen_axcel)

    def _gen_seg(self, ticks):
        ret = u''
        for pos in self.deals.connection.execute("select ticket, direction, count, open_coast, close_coast, broker_comm + stock_comm, open_datetime, close_datetime from positions where id <> -1 order by close_datetime, open_datetime"):
            if not pos[0] in ticks:
                continue
            (open_datetime, close_datetime) = map(lambda a: u'{0:4}.{1:02}.{2:02}'.format(a.year, a.month, a.day), pos[-2:])
            ret += u'{0}\t{1}'.format(pos[0], -1 == pos[1] and 'L' or 'S')
            v = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: self.comma.get_value_as_int() < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, self.comma.get_value_as_int()), pos[2:-2]))
            if self.comma_as_splitter.props.active:
                v = v.replace('.', ',')
            ret += u'\t{0}\t\t\t\t\t\t{1}\t{2}\n'.format(v, open_datetime, close_datetime)
        return ret

    def _gen_axcel(self, ticks):
        ret = u''
        for pos in self.deals.connection.execute("select open_datetime, close_datetime, ticket, direction, open_coast, close_coast, count, open_volume, close_volume from positions where id <> -1 order by close_datetime, open_datetime"):
            if not pos[2] in ticks:
                continue
            vvv = map(lambda a: [u'{0:4}.{1:02}.{2:02}'.format(a.year, a.month, a.day), u'{0:02}:{1:02}:{2:02}'.format(a.hour, a.minute, a.second)], pos[:2])
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), vvv[0] + vvv[1])
            ret += u'\t{0}\t{1}'.format(pos[2], -1 == pos[3] and 'L' or 'S')
            aa = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: self.comma.get_value_as_int() < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, self.comma.get_value_as_int()), pos[4:]))
            if self.comma_as_splitter.props.active:
                aa = aa.replace('.', ',')
            ret += u'\t{0}\n'.format(aa)
            
        return ret

    def clicked(self, button, call_me):
        if hasattr(self, "coats") and self.coats.checked and hasattr(self, "deals") and self.deals.ready:
            bc = []
            self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.get_active() and bc.append(wid.get_label()))
            self.buffer.set_text(call_me(bc))
        else:
            self.show_error(u'Сначала надо указать валидный файл')

    def show_error(self, text):
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = self.window)
        dial.props.text = text
        dial.run()
        dial.destroy()

    def file_set(self, widget):
        try:
            self.coats = sources.xml_parser(widget.get_filename())
        except:
            self.show_error(u'Это походу не xml')
            return

        try:
            self.coats.check_file()
            self.deals = deals_core.deals_proc()
            self.deals.create_new(':memory:')
            self.deals.get_from_source(self.coats)
            self.deals.check_balance()
            self.deals.make_positions()
        except Exception as e:
            self.show_error(traceback.format_exc())
            return

        self.stock_buttons.foreach(self.stock_buttons.remove)
        for (ticket,) in self.deals.connection.execute("select distinct security_name from deals order by security_name"):
            b = gtk.ToggleButton(label = ticket)
            b.set_active(True)
            self.stock_buttons.pack_start(b, False, True, 5)
            self.stock_store.append([ticket])

        resall = gtk.Button(u'Сбросить все')
        resall.connect("clicked", lambda ww: self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(False)))
        self.stock_buttons.pack_end(resall, False, True)
        invall = gtk.Button(u'Реверс все')
        invall.connect("clicked", lambda ww: self.stock_buttons.foreach(lambda wid: wid.__class__ == gtk.ToggleButton and wid.set_active(not wid.get_active())))
        self.stock_buttons.pack_end(invall, False, True)
        self.show()
            
    def show(self):
        win = self.builder.get_object("main_window")
        win.show_all()

        
if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
