# -*- coding: utf-8 -*-
"""
"""

import sys, os

sys.path.append('..')
from mendeley import API



def main():
    m = API()

#            - 'bib'
#            - 'client'
#            - 'tags'
#            - 'patent'
#            - 'all'
#    
    #wtf = m.documents.get()
    
    #wtf = m.documents.get(view='bib')

    #wtf = m.documents.get(view='client')
     
    wtf = m.documents.get(view='tags')
    
    wtf2 = [x.id for x in wtf]    
    
    d = wtf.docs
    print(d[0])
    import pdb
    pdb.set_trace() 
    
    wtf = m.documents.get(view='patent')
    wtf = m.documents.get(view='all')
    
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