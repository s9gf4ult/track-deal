#!/bin/env python
# -*- coding: utf-8 -*-
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
        self.date_view_control = list_view_sort_control(self.date_view, [("id", gtk.CellRendererSpin(), int, "id"), (u'Открытие', gtk.CellRendererText(), str, "open_datetime"), (u'Закрытие', gtk.CellRendererText(), str, "close_datetime"), (u'Количество', gtk.CellRendererSpin(), int, "count")], self_sorting = False, sort_callback = self.resort_date_view)
        self.stock_view_control = list_view_sort_control(self.stock_view, [(u'Инструмент', gtk.CellRendererText(), str, "ticket")], self_sorting = False, sort_callback = self.resort_stock_view)
        

    def update_widget(self):
        pass

    def stock_cursor_changed(self, treeview):
        pass

    def date_cursor_changed(self, treeview):
        pass

    def update_blog_text(self):
        pass
    
