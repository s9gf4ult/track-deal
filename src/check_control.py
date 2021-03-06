#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from list_view_sort_control import list_view_sort_control

class check_control():
    """
    \brief controlls widget for checking several elements

    treeview and some buttons to select and deselect one or more elements displayed in treeview, first column will display checkbuttons to select or deselect each element
    """
    
    def __init__(self, treeview, first_column_name, columns, reverse_button = None, reverse_all_button = None, select_button = None, select_all_button = None, deselect_button = None, deselect_all_button = None, list_view_control_class = list_view_sort_control, odd_color = '#FFFFFF', even_color = '#FFFFFF'):
        """
        \param treeview - gtk.TreeView instance
        \param first_column_name - str, name of column with checkbuttons
        \param columns - list of tuples (name, gtk.CellRenderer instance)
        \param reverse_button - gtk.Button instance, selected rows will be reverse selected if clicked
        \param reverse_all_button - all rows will be reverse selected
        \param select_button - selected rows will be selected
        \param select_all_button - all rows will be selected
        \param deselect_button - selected rows will be deselected
        \param deselect_all_button - all rows will be deselected
        \param list_view_control_class - class to use to control treeview
        """
        c = gtk.CellRendererToggle()
        c.props.activatable = True
        c.connect("toggled", self.row_toggled)
        self.list_control = list_view_control_class(treeview, [(first_column_name, c)] + columns, odd_color = odd_color, even_color = even_color)
        self.treeview = treeview
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.reverse_button = reverse_button
        if self.reverse_button:
            self.reverse_button.connect("clicked", self.selection_button_clicked, self.reverse_foreach)
        self.reverse_all_button = reverse_all_button
        if self.reverse_all_button:
            self.reverse_all_button.connect("clicked", self.all_button_clicked, self.reverse_foreach)
        self.select_button = select_button
        if self.select_button:
            self.select_button.connect("clicked", self.selection_button_clicked, self.set_foreach)
        self.select_all_button = select_all_button
        if self.select_all_button:
            self.select_all_button.connect("clicked", self.all_button_clicked, self.set_foreach)
        self.deselect_button = deselect_button
        if self.deselect_button:
            self.deselect_button.connect("clicked", self.selection_button_clicked, self.unset_foreach)
        self.deselect_all_button = deselect_all_button
        if self.deselect_all_button:
            self.deselect_all_button.connect("clicked", self.all_button_clicked, self.unset_foreach)

    def set_odd_color(self, odd_color):
        """\brief 
        \param odd_color
        """
        self.list_control.set_odd_color(odd_color)

    def set_even_color(self, even_color):
        """\brief 
        \param even_color
        """
        self.list_control.set_even_color(even_color)

    def row_toggled(self, renderer, path):
        row = self.list_control.get_row_by_path(path)
        self.list_control.save_value_by_path(path, 0, not row[0])
        
    def reverse_foreach(self, x, y, i):
        m = self.list_control.get_model()
        row = self.list_control.get_row_by_iter(i)
        self.list_control.save_value_by_iter(i, 0, not row[0])

    def unset_foreach(self, x, u, i):
        self.list_control.save_value_by_iter(i, 0, False)

    def set_foreach(self, x, y, i):
        self.list_control.save_value_by_iter(i, 0, True)
        
    def selection_button_clicked(self, bt, callme):
        self.treeview.get_selection().selected_foreach(callme)

    def all_button_clicked(self, bt, callme):
        self.treeview.get_model().foreach(callme)


    def flush_list(self):
        self.list_control.make_model()

    def update_rows(self, rows, default_toggle = True):
        """
        \brief update rows in treeview to display and select
        \param rows - list of tuples to replace the rows in treeview with, first column (boolean signaling selected or not) of each row must be skiped 
        \param default_toggle - boolean, toggle new created rows or do not
        """
        if not self.list_control.get_model():
            self.list_control.make_model()
        rws = self.list_control.get_rows()
        found = {}
        for rw in rws:
            found[tuple(map(lambda a: isinstance(a, str) and a.decode("utf-8") or a, rw[1:]))] = rw[0]
        new = []
        for row in rows:
            x = tuple(map(lambda a: isinstance(a, str) and a.decode("utf-8") or a, row))
            if found.has_key(x):
                new.append(tuple([found[x]] + list(x)))
            else:
                new.append(tuple([default_toggle] + list(x)))
        self.list_control.update_rows(new)

    def get_checked_rows(self):
        """
        \brief return just selected rows
        \retval [] if no one row is selected
        \retval list of tuples (*data fields)
        """
        checked = self.list_control.get_rows()
        return map(lambda a: a[1:], filter(lambda c: c[0], checked))


if __name__ == "__main__":
    def update_rows(bt, con, rows):
        con.update_rows(rows)
        
    w = gtk.Dialog()
    p = w.get_content_area()
    v = gtk.TreeView()
    p.pack_start(v)
    sa = gtk.Button("select all")
    ss = gtk.Button("select")
    da = gtk.Button("deselect all")
    dd = gtk.Button("deselect")
    ra = gtk.Button("reverse all")
    rr = gtk.Button("reverse")
    ub = gtk.Button("rows 1")
    ubb = gtk.Button("rows 2")
    t = gtk.Entry()
    bbt = gtk.Button("show checked")
    for wid in [sa, ss, da, dd, ra, rr, ub, ubb, t, bbt]:
        p.pack_start(wid, False)
    con = check_control(v, "Yes?", [("Name", gtk.CellRendererText()), ["FUCK YOU", str]], select_button = ss, select_all_button = sa, deselect_button = dd, deselect_all_button = da, reverse_button = rr, reverse_all_button = ra)
    con.list_control.update_rows([(True, "One", ""), (False, "Two", ""), (True, "2 + 2 = 4", ""), (False, "3*5 = 14", "is false"), (True, "jojojo", "camon camon")])
    ub.connect("clicked", update_rows, con, [("ROW 1", "hesell"), ("ROW 2", "fjfj"), ("row 3",""), ("row 4","")])
    ubb.connect("clicked", update_rows, con, [("ROW 1", "haskell"), ("ROW 2", "fjfj"), ("ROW 3","")])
    def bbtclicked(bt):
        t.set_text("{0}".format(con.get_checked_rows()))
    bbt.connect("clicked", bbtclicked)
    w.show_all()
    w.run()
