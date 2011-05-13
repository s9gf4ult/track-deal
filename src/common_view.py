#!/bin/env python
# -*- coding: utf-8 -*-
## common_view ##
from common_model import common_model

class common_view(object):
    """abstract class for view
    """
    _model = None
    
    def __init__(self):
        """
        """
        
        raise NotImplementedError()

    def set_model(self, model):
        """sets _model variable in view
        
        Arguments:
        - `model`:
        """
        assert(isinstance(model, common_model))
        self._model = model

    def get_model(self):
        """gets model
        
        Arguments:
        - `model`:
        """
        return self._model


    def run(self, ):
        """run the view
        """
        raise NotImplementedError()
