# -*- coding: utf-8 -*-
"""
Example function calls
"""

import pdb

from mendeley import client_library
from mendeley import API

doi = '10.1177/1073858414541484'

temp = client_library.UserLibrary(verbose=True)

m = API()

import pickle
libname = 'data/client_library/karmentrout11@gmailcom.pickle'
f = open(libname, 'rb')
b = pickle.load(f)

#pdb.set_trace()

file = temp.get_single_paper('10.1177/1073858414541484')

pdb.set_trace()


"""
#This is old code
#------------------------------------------------------------------------------

um  = mapi.UserMethods()
wtf = um.docs_get_details()
import pdb
pdb.set_trace()
wtf = um.profile_get_info()
#wtf = um.docs_get_library_ids(get_all=True)



#4 Public Testing
#-------------------------------
#pc = auth.get_public_credentials()
#pm = mapi.PublicMethods()
#ta = pm.get_top_authors()

import pdb
pdb.set_trace()

#
##wtf = pm.get_entry_details(10461217,'pmid')
##wtf = pm.get_entry_details(12345,'pmid')
#import pdb
#pdb.set_trace()
#
#pm.search_Mendeley_catalog('Year:2007 Author:Grill') #Nothing :/




#pdb.set_trace()
"""