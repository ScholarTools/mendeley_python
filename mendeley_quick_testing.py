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

def test_get_pdf(pdf_url):
    import requests
    resp = requests.get(pdf_url)
    if 'text/html' in resp.headers['Content-Type']:
        with open('test_file.html', 'wb') as file:
            file.write(resp.content)
    else:
        with open('test_pdf.pdf', 'wb') as file:
            file.write(resp.content)


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

ae = dict()
ae["title"] = 'CRISPR/Cas9-mediated genome engineering: An adeno-associated viral (AAV) vector toolbox'
ae["type"] = 'journal'
ae["identifiers"] = {"doi" : '10.1002/biot.201400046'}
m.documents.create(ae)
'''

actual_doc = temp.get_document('10.1002/biot.201400046')
doc = temp.get_document('10.1038/nrg3686')
print(doc)
import pdb
pdb.set_trace()
#return_bundle = actual_doc.add_all_references()

#print(return_bundle)
#print('total number of references: ' + str(return_bundle['total_refs']))
#print('refs without DOIs: ' + str(return_bundle['without_dois']))



'''
doc_data = random_entry()
print(doc_data['title'])

cj = m.documents.create(doc_data)
print(cj)
'''

nature_pdf_url = 'http://www.nature.com/nrg/journal/v15/n5/pdf/nrg3686.pdf'
from pypub.publishers.pub_objects import Nature
#pdf_content = Nature.get_pdf_content(nature_pdf_url)
#adding_file = {'file' : pdf_content}
#cj.add_file(adding_file)

'''
if 'pdf' in resp.headers['content-type']:
    with open('nature_test_pdf.pdf', 'wb') as file:
        file.write(pdf_content)
else:
    with open('nature_test_html.html', 'wb') as file:
        file.write(pdf_content)
'''


#added = cj.addfile_from_url(file_url)
#print(added)

test_file = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400828/pdf'
wy_test_file = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/pdf'
sd_test_file = 'http://ac.els-cdn.com/S0006899313013048/1-s2.0-S0006899313013048-main.pdf?_tid=d0627c6c-22b6-11e6-bf6e-00000aab0f27&acdnat=1464208105_97b45bc2a955e54bd12cadd26e2e053c'
sp_test_file = 'http://download.springer.com/static/pdf/60/art%253A10.1007%252Fs10514-015-9513-5.pdf?originUrl=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%2Fs10514-015-9513-5&token2=exp=1464211096~acl=%2Fstatic%2Fpdf%2F60%2Fart%25253A10.1007%25252Fs10514-015-9513-5.pdf%3ForiginUrl%3Dhttp%253A%252F%252Flink.springer.com%252Farticle%252F10.1007%252Fs10514-015-9513-5*~hmac=f82c4baeb735331580f20ab0b694b73a749fcbe905fdaf1a3821c2327a7b12c7'

#test_get_pdf(sp_test_file)

#added = cj.addfile_from_url(sp_test_file)
#print(added)

'''
file = {'file': open('test.pdf', 'rb')}
added = cj.addfile(file)

print(added)
'''

#document = temp.get_document('10.1177/1073858414541484')
#print(document)
#document.addfile(file)

#file = {'file': open('test.pdf', 'rb')}
#api.Files.linkfile(api.Files, file, document.json)
