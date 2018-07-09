# -*- coding: utf-8 -*-
"""
Created on Thu July 05 11:10:30 2018

@author: ojs1g14
"""


def add_docs(input_file):
    """
    docstring yo
    """
    f = open(input_file, r+)
    for line in f.readlines():
        if "def " in line:
            print(str(line))
    
    f.close()