#!/bin/env python
# -*- coding: utf-8 -*-
## sconnection_test ##

import random
import unittest
import sconnection


class sconnection_test(unittest.TestCase):
    """tests `sconnection` methods
    Attributes:
    
    """
    ##############
    # Attributes #
    ##############
    
    
    ###########
    # Methods #
    ###########
    
    def setUp(self, ):
        """
        """
        self.conn = sconnection.sconnection(":memory:")
        


if __name__ == '__main__':
    unittest.main()
