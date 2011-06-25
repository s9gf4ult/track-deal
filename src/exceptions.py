#!/bin/env python
# -*- coding: utf-8 -*-
## exceptions ##

class od_exception(Exception):
    """The common exception of open deals
    Attributes:
    
    """
    pass

class od_exception_db_error(od_exception):
    """The common database exception in open deals
    Attributes:
    
    """
    pass

class od_exception_db_closed(od_exception_db_error):
    """Trys operation when database is closed
    Attributes:
    
    """
    pass

class od_exception_db_opened(od_exception_db_error):
    """Try's open new database when there is opened one
    Attributes:
    
    """
    pass

class od_exception_decorator(od_exception):
    """Exception in decorator
    Attributes:
    
    """
    pass
        
class od_exception_action_error(od_exception):
    pass

class od_exception_action_cannot_create(od_exception_action_error):
    def __init__(self, actions_above):
        """
        Arguments:
        \param actions_above 
        """
        super(od_exception_action_cannot_create, self).__init__()
        self.__actions_above__ = actions_above

class od_exception_action_does_not_exists(od_exception_action_error):
    pass


        

        
