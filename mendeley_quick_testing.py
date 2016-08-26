# -*- coding: utf-8 -*-
"""
Example function calls
"""

import string
import random
import sys
import os
import json

from PyQt5.QtWidgets import *
import requests

from mendeley import client_library
from mendeley import api
from database import db_logging as db
from mendeley import integrity

def random_entry():
    d = dict()
    d["title"] = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(8))
    d["type"] = 'journal'
    d["identifiers"] = dict()
    d["identifiers"]["doi"] = '10.' + str(random.random())[2:12]
    d["tags"] = ["cool paper"]
    return d


def test_get_pdf(pdf_url):
    resp = requests.get(pdf_url)
    if 'text/html' in resp.headers['Content-Type']:
        with open('test_file.html', 'wb') as file:
            file.write(resp.content)
    else:
        with open('test_pdf.pdf', 'wb') as file:
            file.write(resp.content)


def _file_selector():
        app = QApplication(sys.argv)
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDirectory(os.path.expanduser('~'))
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            return filenames[0]
        else:
            return None


def annotation_maker(document_id):
    ann = dict()
    ann['type'] = 'sticky_note'
    ann['color'] = {'g': 0, 'b': 173, 'r': 255}
    ann['document_id'] = document_id
    ann['privacy_level'] = 'private'
    ann['positions'] = [{'page': 1, 'top_left': {'y': 500, 'x': 120}, 'bottom_right': {'y': 500, 'x': 120}}]
    ann['text'] = 'test post please ignore'
    return ann

sd1 = {'title': 'All fields present', 'type': 'journal', 'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}],
           'tags': ['generated'], 'identifiers': {'doi': '10.1111'}, 'keywords': ['Longclaw', 'Nights Watch'],
           'pages': '1-10'}


doi = '10.1177/1073858414541484'
doi = '10.1002/bit.25159'
doi_for_file = '10.1002/biot.201400046'

temp = client_library.UserLibrary(verbose=True)
m = api.API()

# analyst = integrity.Analysis(temp)
# analyst.validate_dois()

# temp.update_file_from_local(doi=doi)

import pdb
pdb.set_trace()


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

#actual_doc = temp.get_document('10.1002/biot.201400046')
#doc = temp.get_document('10.1111/j.1464-4096.2004.04875.x')
#print(doc)

#return_bundle = actual_doc.add_all_references()

#print(return_bundle)
#print('total number of references: ' + str(return_bundle['total_refs']))
#print('refs without DOIs: ' + str(return_bundle['without_dois']))


#doc_data = random_entry()
#print(doc_data)



# db_doi = '10.1111/j.1748-1716.1980.tb06578.x'
# db_doc = db.get_saved_info(db_doi)
# m_doc = temp.get_document(db_doi)



test_file = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400828/pdf'
wy_test_file = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/pdf'
sd_test_file = 'http://ac.els-cdn.com/S0006899313013048/1-s2.0-S0006899313013048-main.pdf?_tid=d0627c6c-22b6-11e6-bf6e-00000aab0f27&acdnat=1464208105_97b45bc2a955e54bd12cadd26e2e053c'
sp_test_file = 'http://download.springer.com/static/pdf/60/art%253A10.1007%252Fs10514-015-9513-5.pdf?originUrl=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%2Fs10514-015-9513-5&token2=exp=1464211096~acl=%2Fstatic%2Fpdf%2F60%2Fart%25253A10.1007%25252Fs10514-015-9513-5.pdf%3ForiginUrl%3Dhttp%253A%252F%252Flink.springer.com%252Farticle%252F10.1007%252Fs10514-015-9513-5*~hmac=f82c4baeb735331580f20ab0b694b73a749fcbe905fdaf1a3821c2327a7b12c7'

