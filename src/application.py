#!/bin/env python
# -*- coding: utf-8 -*-
## application ##
from common_model import common_model
from common_view import common_view

class application(object):
    """Open deals application class
    """
    
    def __init__(self, view):
        """Creates new instance of application
        
        
        Arguments:
        - `view`: the instance of view
        """
        assert(isinstance(view, common_view))
        self._view = view

    def start(self, model = None):
        """starts the application
        
        Arguments:
        - `model`:posible model to open with view
        """
        if model:
            assert(isinstance(model, common_model))
            self._view.set_model(model)
        self._view.run()
        self.exit()

    def exit(self, ):
        """
        """
        pass
    
