#!/bin/env python
# -*- coding: utf-8 -*-
## sqlite_model ##

from common_model import common_model
from common_view import common_view
from sconnection import sconnection
from common_methods import *

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

    @raise_db_opened
    def connect(self, connection_string):
        """connects to file or memory
        
        Arguments:
        - `connection_string`:
        """
        assert(isinstance(connection_string, basestring))
        self._connection_string = connection_string
        self._sqlite_connection = sconnection(connection_string)

    @raise_db_closed
    def dbinit(self, ):
        """
        initializes new database
        """
        with open('./sqlite/dbinit.sql') as ofile:
            self._sqlite_connection.executescript(ofile.read())

    @raise_db_closed
    def dbtemp(self, ):
        """
        initalizes temporary objects in database
        """
        with open('./sqlite/dbtemp.sql') as ofile:
            self._sqlite_connection.executescript(ofile.read())

    @raise_db_opened
    def open_existing(self, filename):
        """
        Opens existing database from file
        Arguments:
        - `filename`:
        """
        self.connect(filename)
        self.dbtemp()

    @raise_db_closed
    def disconnect(self, ):
        """Disconnects from the database
        """
        self._sqlite_connection.close()
        self._sqlite_connection=None


    @raise_db_closed
    def begin_transaction(self, ):
        """Begins transaction
        """
        self._sqlite_connection.begin_transaction()

    @raise_db_closed
    def commit(self, ):
        """Commits
        """
        self._sqlite_connection.commit()

    @raise_db_closed
    def rollback(self, ):
        """Rollback
        """
        self._sqlite_connection.rollback()




        
        
        

