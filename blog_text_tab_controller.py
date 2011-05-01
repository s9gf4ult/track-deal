#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from list_view_sort_control import list_view_sort_control

class blog_text_tab_controller:
    def __init__(self, database, builder):
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)

        self.database = database
        self.builder = builder
        shorter("stock_view", "cursor-changed", self.stock_cursor_changed)
        shorter("date_view", "cursor-changed", self.date_cursor_changed)
        self.blog_text = self.builder.get_object("blog_text_view")
        self.stock_view = self.builder.get_object("stock_view")
        self.date_view = self.builder.get_object("date_view")
        self.date_view_control = list_view_sort_control(self.date_view, [("id", gtk.CellRendererSpin(), int, "id"), (u'Открытие', gtk.CellRendererText(), str, "open_datetime"), (u'Закрытие', gtk.CellRendererText(), str, "close_datetime"), (u'Направление', gtk.CellRendererText(), str, "direction"),  (u'Количество', gtk.CellRendererSpin(), int, "count")], self_sorting = False, sort_callback = self.resort_date_view)
        self.stock_view_control = list_view_sort_control(self.stock_view, [(u'Инструмент', gtk.CellRendererText(), str, "ticket")], self_sorting = False, sort_callback = self.resort_stock_view)
        self.stocks_sort_val = "ticket"
        self.datetime_sort_val = "close_datetime"
        

    def update_widget(self):
        if self.database.connection == None:
            self.stock_view_control.update_rows([])
            self.date_view_control.update_rows([])
            self.blog_text.get_buffer().set_text("")
            return
        self.draw_stocks()

    def stock_cursor_changed(self, treeview):
        self.draw_dates()

    def date_cursor_changed(self, treeview):
        self.update_blog_text()

    def update_blog_text(self):
        if not self.database.connection:
            return
        (path, col) = self.date_view.get_cursor()
        if path != None:
            m = self.date_view.get_model()
            it = m.get_iter(path)
            self.blog_text.get_buffer().set_text(self._get_text_for_blog(m.get_value(it, 0)))

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
        
    
    def draw_stocks(self):
        if not self.database.connection:
            return
        self.stock_view_control.update_rows(self.database.connection.execute("select distinct ticket from positions order by {0}".format(self.stocks_sort_val)))

    def draw_dates(self):
        if self.database.connection == None:
            return
        (path, col) = self.stock_view.get_cursor()
        if path != None:
            m = self.stock_view.get_model()
            ticket = m.get_value(m.get_iter(path), 0)
            def one(a):
                ret = list(a)
                if a[3] < 0:
                    ret[3] = "LONG"
                elif a[3] > 0:
                    ret[3] = "SHORT"
                return tuple(ret)
            x = map(one, self.database.connection.execute("select id, open_datetime, close_datetime, direction, count from positions where ticket = ? order by {0}".format(self.datetime_sort_val), (ticket, )))
            self.date_view_control.update_rows(x)

    def resort_stock_view(self, col, order, params):
        if order == gtk.SORT_ASCENDING:
            self.stocks_sort_val = params[0]
        elif order == gtk.SORT_DESCENDING:
            self.stocks_sort_val = params[0] + " desc"
        self.draw_stocks()

    def resort_date_view(self, col, order, params):
        if order == gtk.SORT_ASCENDING:
            self.datetime_sort_val = params[0]
        elif order == gtk.SORT_DESCENDING:
            self.datetime_sort_val = params[0] + " desc"    
        self.draw_dates()
