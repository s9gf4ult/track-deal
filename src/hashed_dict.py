#!/bin/env python
# -*- coding: utf-8 -*-
## hashed_dict ##

class hashed_dict(dict):
    def __hash__(self, ):
        if len(self) == 0:
            return ''.__hash__()
        else:
            keys = self.keys()
            keys.sort()
            return reduce(lambda a, b: u'{0},{1}'.format(a, b),
                          map(lambda c: u'{0}:{1}'.format(c, self[c]), keys)).__hash__()
        

        
