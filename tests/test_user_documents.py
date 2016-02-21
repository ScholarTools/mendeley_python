# -*- coding: utf-8 -*-
"""
"""

import sys, os

sys.path.append('..')
from mendeley import API

def main():
    m = API()
    
    wtf = m.documents.get()
    
    import pdb
    pdb.set_trace()

    
    print('Finished running "User Documents" tests')


def field_testing():
    """
    Go through all the documents, look at the json, and compare to the fields
    that are defined in the class
    """
    pass

if __name__ == '__main__':
    print('Running "User Documents" tests')
    main()