#!/bin/env python
# -*- coding: utf-8 -*-

import gtk

class list_view_sort_control:
    """
    \~russian
    \brief Контрол для управления списком элементов.
    
    Реализует сортировку при нажатии на заголовки колонок списка,
    возможен обратный вызов на сортировку, чтобы обновить данные в модели так,
    как это требуется.
    """
    def __init__(self, treeview, columns, self_sorting = True, sort_callback = None):
        """
        \~english
        \param treeview instance of gtk.TreeView
        \param columns must be list of tuples with name, renderer, optionally type,
        and optionally other data assigned to column order of tuple in the list
        determines the order of columns in TreeView
        \param self_sorting can be True or False.
        If True then control will sort list independently. Else sort_callback will be called
        to reload data into model in right order.
        \param sort_callback must be like that lambda column, order, parameters:
                                               column - column which clicked on,
                                               order - gtk.SORT_ASCENDING or gtk.SORT_DESCENDING
                                               parameters - columns[n][3:] where n is a number of column clicked on
        \~russian
        \param treeview TreeView экземпляр
        \param columns список кортежей следующего содержания (name, renderer, type, rest) Где:\n
        \c name - это имя столбца, оно будет отображаться в заголовке TreeView\n
        \c renderer gtk.CellRenderer - рендератор которым будут рисоваться данные в соответствующем столбце TreeView\n
        \c type - тип данных для соответствуюдего столбца модели, будет передаваться в конструктоп ListStore\n
        \c rest - остальные аргументы относящиеся к данному столбцу, будут передаваться в \c sort_callback.
        \param self_sorting - булевое значение. Если истинно, то обработка нажатия на заголовок TreeView будет отрабатываться
        контролом самостоятельно путем выставления sort_column_id в модели.
        \param sort_callback - функция следующих аргументов:\n
        \c column - gtk.TreeViewColumn на которую нажал пользователь\n
        \c order - gtk.SORT_ASCENDING или gtk.SORT_DESCENDING когда нужно отсортировать по возрастанию или по убыванию соответственно\n
        \c rest - остальные аргументы из соответствующего кортежа из \c columns
        \note Если \c self_sorting положительна, то sort_callback может остаться Null
       
        """
        def get3ordefault(tpl, default):
            if len(tpl) < 3:
                return default
            else:
                if tpl[2] != None:
                    return tpl[2]
                else:
                    return default
                
        def getparams(tpl):
            if len(tpl) > 3:
                return tpl[3:]
            else:
                return None
        self.self_sorting = self_sorting
        self.sort_callback = sort_callback
        self.treeview = treeview
        self.model_columns = []
        for k in xrange(0, len(columns)):
            prop = {}
            if isinstance(columns[k][1], gtk.CellRendererText):
                prop["text"] = k
                if isinstance(columns[k][1], gtk.CellRendererSpin):
                    self.model_columns.append(get3ordefault(columns[k], float))
                else:
                    self.model_columns.append(get3ordefault(columns[k], str))
            elif isinstance(columns[k][1], gtk.CellRendererProgress):
                prop["value"] = k
                self.model_columns.append(get3ordefault(columns[k], float))
            elif isinstance(columns[k][1], gtk.CellRendererToggle):
                prop["active"] = k
                self.model_columns.append(get3ordefault(columns[k], bool))
            elif isinstance(columns[k][1], gtk.CellRendererPixbuf):
                prop["pixbuf"] = k
                self.model_columns.append(get3ordefault(columns[k], gtk.gdk.Pixbuf))
            c = gtk.TreeViewColumn(columns[k][0], columns[k][1], **prop)
            c.set_clickable(True)
            c.connect("clicked", self.column_clicked, k, getparams(columns[k]))
            self.treeview.append_column(c)
            
    def make_model(self):
        """\brief make new model and attach it to TreeView"""
        m = self.get_new_store()
        self.treeview.set_model(m)

    def get_new_store(self):
        """\brief create new model
        \return empty ListStore with columns specified in constructor of this class
        """
        return gtk.ListStore(*self.model_columns)
        
    def column_clicked(self, column, col_id, params):
        order = self.toggle_sort_indicator(col_id)
        if order != None:
            if not self.self_sorting:
                if self.sort_callback != None:
                    self.sort_callback(column, order, params)
            else:
                self.treeview.get_model().set_sort_column_id(col_id, order)
            column.set_sort_indicator(True)
            column.set_sort_order(order)
        else:
            column.set_sort_indicator(False)

    def toggle_sort_indicator(self, col_id):
        """
        \~russian
        \brief Переключает состояние стрелочки в заголовке TreeView
        \param col_id номер столбца начиная с 0
        \retval gtk.SORT_ASCENDING стрелочка теперь в состоянии сортировки по возрастанию
        \retval gtk.SORT_DESCENDING по убыванию
        \retval None без сортировки
        \note Этот метод не делает ничего кроме переключения стрелочки, он не сортирует данные
        """
        for col in xrange(0, len(self.treeview.get_columns())):
            if col != col_id:
                self.treeview.get_column(col).set_sort_indicator(False)
        c = self.treeview.get_column(col_id)
        if c.get_sort_indicator():
            if c.get_sort_order() == gtk.SORT_ASCENDING:
                return gtk.SORT_DESCENDING
            else:
                return None
        else:
            return gtk.SORT_ASCENDING
                

    def update_rows(self, rows):
        """
        \~russian
        \brief Заменяет данные в модели
        \param rows список кортежей с данными
        \note метод создает новую модель и привязывает к ней TreeView
        """
        m = self.get_new_store()
        for row in rows:
            m.append(row)
        self.treeview.set_model(m)

    def add_rows(self, rows):
        """
        \~russian
        \brief добавляет данные к модели, предварительно отвязвая ее от TreeView
        \param rows список кортежей с данными для модели
        """
        if not self.treeview.get_model():
            self.make_model()
        m = self.get_model()
        self.treeview.set_model(None)
        for row in rows:
            m.append(row)
        self.treeview.set_model(m)

    def get_model(self):
        """
        \~russian
        \brief возвращает модель привязанную к TreeView
        """
        return self.treeview.get_model()

    def _get_rows_with_filter(self, filterfunc):
        ret = []
        def foreachfunc(model, path, it):
            ret.append(filterfunc(model, path, it))
        self.get_model().foreach(foreachfunc)
        return ret

    def get_rows(self):
        def all_columns(model, path, it):
            l = model.get_n_columns()
            p = []
            for x in xrange(0, l):
                p.append(model.get_value(it, x))
            return tuple(p)
        return self._get_rows_with_filter(all_columns)
            
        

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    v = gtk.TreeView()
    p.pack_start(v)
    con = list_view_sort_control(v, [("OK", gtk.CellRendererToggle()), ("Name", gtk.CellRendererText())])
    con.update_rows([(True, "ijij"), (True, "isejfj"), (False, "jeifjjj2")])
    con.add_rows([(False, "False"), (True, "True"), (True, "is cool"), (False, "is sucks")])
    t = gtk.TextView()
    b = gtk.Button("push")
    def pushed(bt):
        t.get_buffer().set_text("{0}".format(con.get_rows()))
    b.connect("clicked", pushed)
    p.pack_start(t, False)
    p.pack_start(b, False)
    w.show_all()
    w.run()
    
