#!/bin/env python
# -*- coding: utf-8 -*-
## sqlite_model ##

from common_model import common_model
from common_view import common_view
from sconnection import sconnection

class sqlite_model(common_model):
    """
    stores data in sqlite
    :Attributes:
       _connection_string = None
       _sqlite_connection = None
    """
    ##############
    # Attributes #
    ##############
    _connection_string = None
    _sqlite_connection = None
    
    
    ###########
    # Methods #
    ###########
    
    def __init__(self, ):
        """new instance of sqlite_model
        """
        pass

    def connect(self, connection_string):
        """connects to file or memory
        
        Arguments:
        - `connection_string`:
        """
        assert(isinstance(connection_string, basestring))
        self._connection_string = connection_string
        self._sqlite_connection = sconnection(connection_string)

    def dbinit(self, ):
        """
        initializes new database
        """
        with open('./sqlite/dbinit.sql') as ofile:
            self._sqlite_connection.executescript

