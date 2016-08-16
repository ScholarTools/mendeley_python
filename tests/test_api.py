# -*- coding: utf-8 -*-
"""
"""
import sys
from nose import *

from mendeley import API
from mendeley import client_library

sys.path.append('database')

m = API('testing')
lib = client_library.UserLibrary()



'''
List of things to test:
- Create a document, verify it was created
    - Try different combinations of information required to create a document
        - I.e. it won't be created if it's missing a document type or if it's missing a title and identifier
- Update a document, verify it was updated
    - Maybe add notes or tags
- Add/retrieve annotations to a document
- Link a file to a document
- Update the file, verify that annoations are retrieved
- Delete file, verify that there is no longer a file attached
- Try adding a paper with a duplicate DOI
- Move document to trash, verify that it was deleted
'''

doc_list = []


def document_builder():
    # Attributes: title, type, identifiers (dict sub-fields: doi, pmid, etc.), abstract, keywords (list),
    # authors (dict sub-fields: first_name, last_name), pages, volume, issue, publisher, editors, year,
    # month, day, tags (list)

    # The titles here describe the fields that are missing.
    d1 = {'title': 'All fields present', 'type': 'journal', 'authors': {'first_name': 'Jon', 'last_name': 'Snow'},
          'tags': 'generated', 'identifiers': {'doi': '10.1111'}, 'keywords': ['Longclaw', 'Nights Watch'],
          'pages': '1-10'}
    d2 = {'title': 'No type', 'authors': {'first_name': 'Jon', 'last_name': 'Snow'}, 'tags': 'generated',
          'identifiers': {'doi': '10.2222'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    d3 = {'title': 'No authors', 'type': 'journal', 'tags': 'generated',
          'identifiers': {'doi': '10.3333'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    d4 = {'title': 'No identifiers', 'type': 'journal', 'authors': {'first_name': 'Jon', 'last_name': 'Snow'},
          'tags': 'generated', 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    d5 = {'title': 'Keywords are not a list', 'type': 'journal', 'authors': {'first_name': 'Jon', 'last_name': 'Snow'},
          'tags': 'generated', 'identifiers': {'doi': '10.5555'}, 'keywords': 'Longclaw, Nights Watch', 'pages': '1-10'}
    d6 = {'type': 'journal', 'authors': {'first_name': 'No', 'last_name': 'Title'}, 'tags': 'generated',
          'identifiers': {'doi': '10.6666'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    d7 = {'title': 'Duplicate DOI', 'type': 'journal', 'authors': {'first_name': 'Jon', 'last_name': 'Snow'},
          'tags': 'generated', 'identifiers': {'doi': '10.1111'}, 'keywords': ['Longclaw', 'Nights Watch'],
          'pages': '1-10'}

    doc_list = [d1, d2, d3, d4, d5, d6, d7]
    # doc_list.append(d1)
    
document_builder()

# Make this a generator
# @with_setup(document_builder)
def test_doc_creation():
    for doc in doc_list:
      yield doc_creator(doc)


# Helper function for test_doc_creation
def doc_creator(new_document):
    doc_data = new_document
    # Not sure this is the best way to do this.
    # Test fails if either the document was not created or
    # the document could not be retrieved
    try:
        m.documents.create(doc_data=doc_data)
        created = m.documents.get(doc_data)
    except Exception:
        assert False
    else:
        if created.json is not None and created.json.get('title') == doc_data.get('title'):
            assert True
        else:
            assert False



def test_doc_update():
    # Add notes or tags
    pass


def test_annotation_retrieval():
    pass


def test_annotation_adding():
    pass


def test_file_linking():
    pass


def test_file_retrieval():
    pass


def test_file_update():
    pass


def test_file_deletion():
    pass


def test_move_doc_to_trash():
    pass


#Document Creation
#-----------------
#1) From user constructed meta
#2) From a file



#Trash testing:
#--------------
#1) Create a document