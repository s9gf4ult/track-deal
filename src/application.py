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
        \param view  the instance of view
        """
        assert(isinstance(view, common_view))
        self._view = view

    def start(self, filename = None):
        """starts the application
        \param model posible model to open with view
        """
        if filename != None:
            self._view.open_existing_sqlite(filename)
        self._view.run()
        self.exit()

    def exit(self, ):
        """exit
        """
        pass

    def get_model(self):
        """Getter for property model
        
        """
        
        return self._view.get_model()

    def set_model(self, model):
        """Setter for property model
        \param model common_model child instance
        """
        assert(isinstance(model, common_model))
        self._view.set_model(model)
