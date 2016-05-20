# -*- coding: utf-8 -*-
"""
Example function calls
"""

import pdb
import string
import random
from mendeley import client_library
from mendeley import API

def random_entry():
    d = dict()
    d["title"] = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))
    d["type"] = 'journal'
    d["identifiers"] = dict()
    d["identifiers"]["doi"] = '10.' + str(random.random())[2:12]
    return d


doi = '10.1177/1073858414541484'

temp = client_library.UserLibrary(verbose=True)
print([x['title'] for x in temp.raw])

m = API()


doc_data = random_entry()

cj = m.documents.create(doc_data)
print(cj)


import pickle
libname = 'data/client_library/karmentrout11@gmailcom.pickle'
f = open(libname, 'rb')
b = pickle.load(f)

#file = temp.get_single_paper('10.1177/1073858414541484')

document = temp.get_document('10.1177/1073858414541484')



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