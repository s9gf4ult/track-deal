#!/bin/env python
# -*- coding: utf-8 -*-
## paper_adder ##

import gtk_view
from list_view_sort_control import list_view_sort_control
from combo_control import combo_control

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
        self.window = shobject("paper_adder")
        self.list = list_view_sort_control(shobject("paper_adder_list"),
                                           [["id", int], ("Имя", gtk.CellRendererText()), ("Тип", gtk.CellRendererText())])
        self.type = combo_select_control(shobject("paper_adder_type"),
                                         answers = [("stock", "Акция"), ("future", "Фьючерс"), ("option", "Опцион")])
        self.stock = combo_control(shobject("paper_adder_stock"))
        
        
        
