#!/bin/env python
# -*- coding: utf-8 -*-
## common_loader ##

class common_loader(object):
    """\brief base class to implement report loaders
    """
    def load(self, model, source):
        """\brief load data from source to model
        \param model - \ref common_model instance, some model to load data into
        \param source - any object describing the source to get data from. Concrete class depends on concrete loader.
        """
        raise NotImplementedError(u'load method of common_loader must be implemented by children')

        
