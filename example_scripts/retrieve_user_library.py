# -*- coding: utf-8 -*-
"""
"""

from mendeley import client_library

#This call relies on information that has been stored in the user config file
c = client_library.UserLibrary(verbose=True)

print(c)

#TODO: If len of docs > 1, print 1st document