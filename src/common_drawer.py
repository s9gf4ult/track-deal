#!/bin/env python
# -*- coding: utf-8 -*-
## common_drawer ##

class common_drawer(object):
    """\brief common class for all drawer must be inherited
    """
    def __init__(self, ):
        """\brief 
        """
        
    def draw(self, context):
        """\brief this method must be implemented by the child to draw something
        \param context - cairo context
        """
        raise NotImplementedError()

