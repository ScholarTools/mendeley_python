# -*- coding: utf-8 -*-
"""
Example function calls
"""

import pdb
import string
import random
from mendeley import client_library
from mendeley import api

def random_entry():
    d = dict()
    d["title"] = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))
    d["type"] = 'journal'
    d["identifiers"] = dict()
    d["identifiers"]["doi"] = '10.' + str(random.random())[2:12]
    d["tags"] = ["cool paper"]
    return d


doi = '10.1177/1073858414541484'

temp = client_library.UserLibrary(verbose=True)
print([x['title'] for x in temp.raw])

m = api.API()

#m.folders.create('New Folder')

# Adding a real entry
'''
ae = dict()
ae["title"] = 'Bioengineering Virus-Like Particles As Vaccines'
ae["type"] = 'journal'
ae["identifiers"] = {"doi" : '10.1002/bit.25159'}
m.documents.create(ae)
'''

actual_doc = temp.get_document('10.1002/bit.25159')
info = actual_doc.add_all_references()

print(info)

'''
doc_data = random_entry()
print(doc_data['title'])

cj = m.documents.create(doc_data)
print(cj)
'''

file_url = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/pdf'
#file_url = 'http://onlinelibrary.wiley.com/store/10.1002/biot.201400046/asset/1402_ftp.pdf?v=1&t=iols4jud&s=c71a3807e2f8bc28879fc93140fdc378fe1b86e1'
#added = cj.addfile_from_url(file_url)
#print(added)

#pdb.set_trace()

'''
file = {'file': open('test.pdf', 'rb')}
added = cj.addfile(file)

print(added)
'''

'''
import pickle
libname = 'data/client_library/karmentrout11@gmailcom.pickle'
f = open(libname, 'rb')
b = pickle.load(f)
'''

document = temp.get_document('10.1177/1073858414541484')
print(document)
#document.addfile(file)

#file = {'file': open('test.pdf', 'rb')}
#api.Files.linkfile(api.Files, file, document.json)


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