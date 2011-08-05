#!/bin/env python
# -*- coding: utf-8 -*-
## od_exceptions ##

class od_exception(Exception):
    """\brief The common exception of open deals
    """
    pass

class od_exception_config_error(od_exception):
    """\brief common config error
    """

class od_exception_config_key_error(od_exception_config_error):
    """\brief getting key error
    """

class od_exception_report_error(od_exception):
    """\brief the common exception of imporing the report
    """
    pass
        
class od_exception_db_error(od_exception):
    """\breif The common database exception in open deals
    """
    pass

class od_exception_db_closed(od_exception_db_error):
    """\brief must be raised when try operation on database which is closed or does not exists
    """
    pass

class od_exception_db_opened(od_exception_db_error):
    """\brief must be raised when try open new database and there is opened one
    """
    pass

class od_exception_decorator(od_exception):
    """Exception in decorator
    """
    pass
        
class od_exception_action_error(od_exception):
    """
    \brief common action error
    """
    pass

class od_exception_action_cannot_create(od_exception_action_error):
    """
    \brief must be raised when trying create new action and the current state not in the end of actions list
    """
    def __init__(self, actions_above):
        """
        \param actions_above 
        """
        super(od_exception_action_cannot_create, self).__init__()
        self.__actions_above__ = actions_above

class od_exception_action_does_not_exists(od_exception_action_error):
    pass
