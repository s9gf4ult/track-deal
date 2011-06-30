#!/bin/env python
# -*- coding: utf-8 -*-
## currency_edit_control ##

class currency_edit_control(object):
    """\~russian
    \brief Контрол для редактирования списка известных валют
    """
    def __init__(self, parent):
        """
        \param parent instance of \ref gtk_view.gtk_view
        """
        self._parent = parent
