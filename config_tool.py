# -*- coding: utf-8 -*-
__author__ = "yangtao"

import os
import sys
import ast
import configparser




class Config:
    def __init__(self, config_file=None):
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),
                                            "config.ini")
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            open(self.config_file, 'w')
        self.config.read(self.config_file)

    def set(self, section: str=None, option: str=None, value: str=None):
        if section:
            if not self.config.has_section(section):
                self.config.add_section(section)
            if option:
                try:
                    value = str(value)
                except:
                    value = ""
                # if isinstance(bool, value):
                #     value = str(value)
                # elif not value:
                #     value = ""
                # else:
                #     value = str(value)
                self.config.set(section, option, value)
        # write
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def __literal_eval(self, node_or_string):
        try:
            return ast.literal_eval(node_or_string)
        except:
            return node_or_string

    def get(self, section: str=None, option: str=None):
        self.config.read(self.config_file)
        if section:
            if option:
                return self.__literal_eval(self.config.get(section, option, fallback=None))
            else:
                if self.config.has_section(section):
                    option_dict = {}
                    for k, v in dict(self.config[section].items()).items():
                        option_dict[k] = self.__literal_eval(v)
                    return option_dict
        else:
            d = dict(self.config._sections)
            for k, v in d.items():
                d[k] = dict(self.__literal_eval(v))
            return d
