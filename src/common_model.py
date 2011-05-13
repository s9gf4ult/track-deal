#!/bin/env python
# -*- coding: utf-8 -*-
## common_model ##

class common_model(object):
    """abstract model class
    """
    _update_callback = None
    
    def __init__(self, ):
        """not implemented model constructor
        """
        
        raise NotImplementedError()

    def connect(self, connect_string):
        """connects to existing database and do not do anything
        
        Arguments:
        - `connect_string`:
        """
        raise NotImplementedError()

    def disconnect(self, ):
        """disconnect from database
        """
        raise NotImplementedError()


    def dbinit(self, ):
        """itialize new empty database
        """
        raise NotImplementedError()

    def dbtemp(self, ):
        """initializes temporary objects in database
        """
        raise NotImplementedError()
    

    def set_update_callback(self, update_callback):
        """Setter for property update_callback
        
        
        Arguments:
        - `update_callback`:
        """
        assert(hasattr(update_callback, "__call__"))
        self._update_callback = update_callback

    def get_update_callback(self):
        """Getter for property update_callback
        
        """
        
        return self._update_callback

    def call_update_callback(self, ):
        """this must be executed when data has changed
        """
        if self._update_callback != None:
            self._update_callback()




