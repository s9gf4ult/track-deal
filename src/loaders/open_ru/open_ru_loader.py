#!/bin/env python
# -*- coding: utf-8 -*-
## open_ru_loader ##

from common_loader import common_loader
import sys

class open_ru_loader(common_loader):
    """\brief loader for open.ru
    """
    def load(self, model, source):
        """\brief 
        \param model
        \param source
        """
        deals = self.get_deals(source)
        account_io = self.get_account_ios(source)
        repo_deals = self.get_repo_deals(source)
        if len(deals + repo_deals) == 0:
            sys.stderr.write('open_ru_loader: There is no one deal in the report {0}\n'.format(source.get_filename()))
            return True
        papers = []
        if source.get_load_repo():
            papers = self.get_papers(deals + repo_deals)
        else:
            papers = self.get_papers(deals)
