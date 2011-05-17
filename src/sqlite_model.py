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

    @raise_db_opened
    def create_new(self, filename):
        """Creates new empty database
        Arguments:
        - `filename`:
        """
        self.connect(filename)
        self.dbinit()
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

    @raise_db_closed
    @in_transaction
    def add_global_data(self, parameters):
        """adds global data and
        Arguments:
        - `parameters`: hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("global_data", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names))) 

    @raise_db_closed
    def get_global_data(self, name):
        """returns value of global data or None if there is no one
        Arguments:
        - `name`:
        """
        ret = self._sqlite_connection.execute_select("select value from global_data where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

    @raise_db_closed
    @in_transaction
    def remove_global_data(self, name):
        """Removes global parameters
        Arguments:
        - `name`: string or list of strings to remove
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from global_data where name = ?", name)

    @raise_db_closed
    def list_global_data(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from global_data"))

    @raise_db_closed
    @in_transaction
    def add_database_attributes(self, parameters):
        """adds database attributes and
        Arguments:
        - `parameters`: hash with name of parameter and value
        """
        names = parameters.keys()
        self._sqlite_connection.insert("database_attributes", map(lambda a, b: {"name" : a, "value" : b}, names, map(lambda x: parameters[x], names))) 

    @raise_db_closed
    def get_database_attribute(self, name):
        """returns value of global parameter or None if there is no one
        Arguments:
        - `name`:
        """
        ret = self._sqlite_connection.execute_select("select value from database_attributes where name = ?", [name]).fetchall()
        if len(ret) > 0:
            return ret[0]["value"]
        else:
            return None

    @raise_db_closed
    @in_transaction
    def remove_database_attribute(self, name):
        """Removes global parameters
        Arguments:
        - `name`: string or list of strings to remove
        """
        if isinstance(name, basestring):
            name = [(name, )]
        else:
            name = map(lambda a: (a, ), name) 
        self._sqlite_connection.executemany("delete from database_attributes where name = ?", name)

    @raise_db_closed
    def list_database_attributes(self, ):
        """Returns list of names of global parameters
        """
        return map(lambda a: a[0], self._sqlite_connection.execute("select name from database_attributes"))
    
    @raise_db_closed
    @in_transaction
    def create_paper(self, type, name, stock = None, class_name = None, full_name = None):
        """creates new paper and returns it's id
        
        Arguments:
        - `type`:
        - `name`:
        - `stock`:
        - `class_name`:
        - `full_name`:
        """
        return self._sqlite_connection.insert("papers", {"type" : type,
                                                         "stock" : stock,
                                                         "class" : class_name,
                                                         "name" : name,
                                                         "full_name" : full_name}).lastrowid

    @raise_db_closed
    def get_paper(self, type_or_id):
        """returns paper by name or by id
        if there is no one returns None
        Arguments:
        - `type_or_id`:
        """
        ret = None
        if isinstance(type_or_id, basestring):
            ret = self._sqlite_connection.execute_select("select * from papers where name = ?", [type_or_id])
        elif isinstance(type_or_id, int):
            ret = self._sqlite_connection.execute_select("select * from papers where id = ?", [type_or_id])
        return (len(ret) > 0 and ret[0] or None) 
