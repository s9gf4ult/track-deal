#!/bin/env python
# -*- coding: utf-8 -*-
## paper_adder ##

import gtk_view
from list_view_sort_control import list_view_sort_control
from combo_control import combo_control
from combo_select_control import combo_select_control
import sqlite3
import gtk
from common_methods import *

class paper_adder(object):
    """\brief control for dialog adding and editing papers manually
    """
    def __init__(self, parent):
        """\brief 
        \param parent \ref gtk_view.gtk_view instance
        """
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        def shobject(name):
            return self._parent.builder.get_object(name)
        ## gtk.Window instance
        self.window = shobject("paper_adder")
        ## \ref list_view_sort_control.list_view_sort_control instance, represent list of papers
        self.list = list_view_sort_control(shobject("paper_adder_list"),
                                           [["id", int], ("Имя", gtk.CellRendererText()), ("Тип", gtk.CellRendererText())])
        ## \ref combo_select_control.combo_select_control instance, accepts to select one of several types
        self.type = combo_select_control(shobject("paper_adder_type"),
                                         answers = [("stock", "Акция"), ("future", "Фьючерс"), ("option", "Опцион")])
        ## \ref combo_control.combo_control instance 
        self.stock = combo_control(shobject("paper_adder_stock"))
        ## \ref combo_control.combo_control instance 
        self.class_field = combo_control(shobject("paper_adder_class"))
        ## gtk.Entry instance
        self.name = shobject("paper_adder_name")
        fn = shobject("paper_adder_full_name")
        ## gtk.TextBuffer instance
        self.full_name = fn.get_buffer()
        self.add = shobject("paper_adder_add")
        self.delete = shobject("paper_adder_delete")
        self.save = shobject("paper_adder_save")
        self.add.connect("clicked", self.add_clicked)
        self.delete.connect("clicked", self.delete_clicked)
        self.save.connect("clicked", self.save_clicked)
        shobject("paper_adder_list").connect("cursor-changed", self.list_cursor_changed)
        self.window.add_buttons(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.window.set_transient_for(shobject("main_window"))
            

    def run(self, ):
        """\brief show dialog window and save data into database if "save" pressed
        \retval gtk.RESPONSE_ACCEPT
        \retval gtk.RESPONSE_CANCEL
        """
        if not self._parent.connected():
            return
        self._parent.model.start_transacted_action("Edit some papers")
        self.window.show_all()
        ret = self.window.run()
        if ret == gtk.RESPONSE_ACCEPT:
            self._parent.model.commit_transacted_action()
        else:
            self._parent.model.rollback()
        self.window.hide()
        return (ret == gtk.RESPONSE_ACCEPT and ret or gtk.RESPONSE_CANCEL)
        
    def update_adder(self, ):
        """\brief update list of papers in the widget
        """
        if not self._parent.connected():
            return

        papers = self._parent.model.list_papers(["name"])
        self.list.update_rows(map(lambda a: (a["id"], a["name"], a["type"]), papers))
        self.flush_fields()

    def flush_fields(self, ):
        """\brief flush all fields in window
        """
        self.type.set_value(None)
        self.stock.set_value(None)
        self.class_field.set_value(None)
        self.name.set_text("")
        self.full_name.set_text("")
        
    def add_clicked(self, button):
        """\brief add button handler
        \param button gtk.Button
        """
        self.add_new_entry()

    def add_new_entry(self, ):
        if not self._parent.connected():
            return
        if self.check_fields_before_add():
            paper = None
            try:
                paper = self._parent.model.create_paper(self.type.get_value(),
                                                        self.name.get_text(),
                                                        stock = self.stock.get_value(),
                                                        class_name = self.class_field.get_value(),
                                                        full_name = self.full_name.get_text(self.full_name.get_start_iter(), self.full_name.get_end_iter()))
            except sqlite3.IntegrityError:
                pass
            else:
                self.list.add_row((paper, self.name.get_text(), self.type.get_value()))
                self.flush_fields()

    def check_fields_before_add(self, ):
        """\brief check if fields like "name", "full_name" and so on entered correctly
        """
        tt = self.type.get_value()
        nn = self.name.get_text()
        return tt <> None and not is_null_or_empty(nn) and not is_blank(nn)

    def delete_clicked(self, button):
        """\brief delete button handler
        \param button
        """
        self.delete_selected_entry()

    def delete_selected_entry(self, ):
        """\brief delete entry from database and from list of selected one
        """
        if not self._parent.connected():
            return

        row = self.list.get_selected_row()
        if row <> None:
            try:
                self._parent.model.remove_paper(row[0])
            except sqlite3.IntegrityError:
                pass
            else:
                self.list.delete_selected()
                self.flush_fields()

    def save_clicked(self, button):
        """\brief save button handler
        \param button
        """
        self.save_selected_item()

    def save_selected_item(self, ):
        """\brief save date into selected item's database instance 
        """
        if not self._parent.connected():
            return

        row = self.list.get_selected_row()
        if row <> None:
            try:
                self._parent.model.change_paper(row[0],
                                                {"name" : self.name.get_text(),
                                                 "full_name" : self.full_name.get_text(self.full_name.get_start_iter(),
                                                                                       self.full_name.get_end_iter()),
                                                 "type" : self.type.get_value(),
                                                 "stock" : self.stock.get_value(),
                                                 "class" : self.class_field.get_value()})
            except sqlite3.IntegrityError:
                pass
            else:
                self.list.save_value_in_selected(1, self.name.get_text())
                self.list.save_value_in_selected(2, self.type.get_value())


    def list_cursor_changed(self, treeview):
        """\brief paper list cursor changed handler
        \param treeview
        """
        self.fill_fields_from_selected()


    def fill_fields_from_selected(self, ):
        """\brief fill fields in the window from the selected row
        """
        if not self._parent.connected():
            return

        row = self.list.get_selected_row()
        if row <> None:
            paper = self._parent.model.get_paper(row[0])
            self.name.set_text(paper["name"])
            self.type.set_value(paper["type"])
            self.full_name.set_text(paper["full_name"])
            self.stock.set_value(paper["stock"])
            self.class_field.set_value(paper["class"])
