#!/bin/env python
# -*- coding: utf-8 -*-
## exceptions ##

class od_exception(Exception):
    """The common exception of open deals
    Attributes:
    
    """

class od_exception_db_error(od_exception):
    """The common database exception in open deals
    Attributes:
    
    """

class od_exception_db_closed(od_exception_db_error):
    """Trys operation when database is closed
    Attributes:
    
    """

class od_exception_db_opened(od_exception_db_error):
    """Try's open new database when there is opened one
    Attributes:
    
    """
        
        

        

        

        
