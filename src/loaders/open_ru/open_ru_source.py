#!/bin/env python
# -*- coding: utf-8 -*-
## open_ru_source ##

class open_ru_source(object):
    """\brief source object for open_ru_loader
    """
    def __init__(self, filename, account_id, load_repo, load_account_io):
        """\brief 
        \param filename
        \param account_id
        \param load_repo
        \param load_account_io
        """
        self._filename = filename
        self._account_id = account_id
        self._load_repo = load_repo
        self._load_account_io = load_account_io
        
    def get_filename(self):
        """\brief Getter for property filename
        """
        return self._filename

    def get_account_id(self):
        """\brief Getter for property account_id
        """
        return self._account_id

    def get_load_repo(self):
        """\brief Getter for property load_repo
        """
        return self._load_repo

    def get_load_account_io(self):
        """\brief Getter for property load_account_io
        """
        return self._load_account_io
