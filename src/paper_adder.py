#!/bin/env python
# -*- coding: utf-8 -*-
## paper_adder ##

import gtk_view

class paper_adder(object):
    """\brief control for dialog adding and editing papers manually
    """
    def __init__(self, parent):
        """\brief 
        \param parent \ref gtk_view.gtk_view instance
        """
        assert(isinstance(parent, gtk_view.gtk_view))
        self._parent = parent
        
