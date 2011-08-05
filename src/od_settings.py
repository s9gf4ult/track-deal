#!/bin/env python
# -*- coding: utf-8 -*-
## od_settings ##

import json
from re import split
import os
import od_exception
from common_methods import gethash, is_null_or_empty

class settings(object):
    """\brief settings saving class
    """
    _config_data = None
    _default_cinfig_data = None
    def __init__(self, ):
        """\brief constructor
        """
        if os.name == 'posix':
            config_dir = None
            if not is_null_or_empty(gethash(os.environ, 'OD_CONFIG_DIR')):
                config_dir = os.environ['OD_CONFIG_DIR']
            else:
                if not is_null_or_empty(gethash(os.environ, 'HOME')):
                    config_dir = os.path.join(os.environ['HOME'], '.open-deals') # this is default config directory
                else:
                    raise EnvironmentError('There is not HOME environment specified')
        elif os.name == 'nt':
            raise NotImplementedError('There is no code for windoze yet')
        self.config_file = os.path.join(config_dir, 'open-deals.cfg')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.exists(self.config_file):
            self.make_default_config()

    def read_config(self, ):
        """\brief read config file into _config_data
        """
        with open(self.config_file) as f:
            self._config_data = json.decode(f)

    def make_default_config(self, ):
        """\brief create default config
        """
        self._config_data = self._default_cinfig_data
        self.save_config()

    def save_config(self, ):
        """\brief save current config state to file
        """
        with open(self.config_file) as f:
            json.dump(self._config_data, f, indent = 4):
            
    def get_key(self, key_name):
        """\brief return value of the key
        \param key_name - string with key sequence separated by dot
        """
        val = self._config_data
        try:
            for key in map(lambda a: a.strip(), split('.', key_name)):
                val = val[key]
        except KeyError as e:
            raise od_exception.od_exception_config_key_error('There is no such key in config "{0}"'.format(key_name))
        return val
        
    def set_key(self, key_name, value):
        """\brief 
        \param key_name - string, key values separated by dot.
        \param value - value to set
        """
        val = self._config_data
        keys = map(lambda a: a.strip(), re.split('.', key_value))
        for key in keys[:-1]:
            try:
                val = val[key]
            except KeyError:
                val[key] = {}
                val = val[key]
        val[keys[-1]] = value
