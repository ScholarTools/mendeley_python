# -*- coding: utf-8 -*-
"""
"""

if __name__ == '__main__':
    import sys
    sys.path.append('..')

#TODO: Try the import, if it fails, then append the path
from mendeley import client_library

#This call relies on information that has been stored in the user config file
c = client_library.UserLibrary(verbose=True)

print(c)

#TODO: If len of docs > 1, print 1st document