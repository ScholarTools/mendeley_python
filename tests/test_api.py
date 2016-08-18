# -*- coding: utf-8 -*-
"""
"""
import sys
import nose
import json

from mendeley import API
from mendeley import client_library
from mendeley.errors import *

from database import db_logging as db


m = API()
lib = client_library.UserLibrary()

doc_id_list = []

# The dictionaries in failing_doc_list should not be able to be created.
# There is an expected call failure with status code 400 or 500.
# The dictionaries in successful_doc_list should be able to be created.
failing_doc_list = []
successful_doc_list = []


def document_builder():
    # Attributes: title, type, identifiers (dict sub-fields: doi, pmid, etc.), abstract, keywords (list),
    # authors (list of dicts: sub-fields: first_name, last_name), pages, volume, issue, publisher, editors, year,
    # month, day, tags (list)

    # Document creation will fail if the dict is missing the type or the title.
    # It will also fail if a field does not match the expected data type, for example if the keywords
    # are a string rather than a list.

    # Documents that should succeed in creation
    sd1 = {'title': 'All fields present', 'type': 'journal', 'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}],
           'tags': ['generated'], 'identifiers': {'doi': '10.1111'}, 'keywords': ['Longclaw', 'Nights Watch'],
           'pages': '1-10'}
    sd2 = {'title': 'No authors', 'type': 'journal', 'tags': ['generated'],
           'identifiers': {'doi': '10.2222'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    sd3 = {'title': 'No identifiers', 'type': 'journal', 'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}],
           'tags': ['generated'], 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    sd4 = {'title': 'Duplicate DOI', 'type': 'journal', 'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}],
           'tags': ['generated'], 'identifiers': {'doi': '10.1111'}, 'keywords': ['Longclaw', 'Nights Watch'],
           'pages': '1-10'}

    # Documents that should fail in creation
    fd1 = {'title': 'No type', 'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}], 'tags': ['generated'],
           'identifiers': {'doi': '10.3333'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}
    fd2 = {'title': 'Keywords are not a list', 'type': 'journal',
           'authors': [{'first_name': 'Jon', 'last_name': 'Snow'}], 'tags': ['generated'],
           'identifiers': {'doi': '10.4444'}, 'keywords': 'Longclaw, Nights Watch', 'pages': '1-10'}
    fd3 = {'type': 'journal', 'authors': [{'first_name': 'No', 'last_name': 'Title'}], 'tags': ['generated'],
           'identifiers': {'doi': '10.5555'}, 'keywords': ['Longclaw', 'Nights Watch'], 'pages': '1-10'}

    failing_doc_list.extend([fd1, fd2, fd3])
    successful_doc_list.extend([sd1, sd2, sd3, sd4])


def cleanup():
    for doc in successful_doc_list:
        identifiers = doc.get('identifiers')
        if identifiers is not None:
            doi = identifiers.get('doi')
            title = None
        else:
            doi = None
            title = doc.get('title')

        db.delete_info(doi=doi, title=title)

    for doc_id in doc_id_list:
        m.documents.move_to_trash(doc_id=doc_id)


document_builder()

# Store the document with all fields in a separate variable
# for ease and consistency of access
full_doc = successful_doc_list[0]


# Make this a generator
# @with_setup(document_builder)
def test_doc_creation():
    for doc in successful_doc_list:
        yield doc_creator, doc
    for doc in failing_doc_list:
        yield failing_doc_creator, doc


# Helper function for test_doc_creation
def doc_creator(new_document):
    doc_data = new_document
    # Not sure this is the best way to do this.
    # Test fails if either the document was not created or
    # the document could not be retrieved
    try:
        m.documents.create(doc_data=doc_data)
        created = m.documents.get(**doc_data)
        doc_id_list.append(created.json[0].get('id'))
    except Exception as exc:
        assert False, str(exc)
    else:
        if created.json is not None and created.json[0].get('title') == doc_data.get('title'):
            pass
        else:
            assert False


def failing_doc_creator(new_document):
    # This function handles the dictionaries that are known to raise
    # an error when trying to create a new document. This test then
    # will pass if the document fails to be created.
    doc_data = new_document
    try:
        m.documents.create(doc_data=doc_data)
    except CallFailedException as exc:
        if '400' in str(exc) or '500' in str(exc):
            pass
        else:
            assert False, 'Call failed with unexpected error: ' + str(exc)
    else:
        assert False, 'Incomplete document was created somehow?'


def test_doc_update():
    # Add notes
    notes = {'notes': 'Test notes.'}
    try:
        m.documents.update(doc_id=doc_id_list[0], new_data=notes)
    except Exception as exc:
        assert False, str(exc)
    else:
        updated = m.documents.get(**full_doc, view='all')
        notes = updated.json[0].get('notes')
        if notes is None or notes != 'Test notes.':
            assert False, notes
        else:
            pass


def test_file_linking():
    with open('hello_world.pdf', 'rb') as file:
        content = file.read()
    try:
        m.files.link_file(file=content, params={'id': doc_id_list[0]})
        updated = m.documents.get(**full_doc)
        has_file = updated.json[0].get('file_attached')
    except Exception as exc:
        assert False, str(exc)
    else:
        if has_file:
            pass
        else:
            assert False, 'File unsuccessfully attached.'


def test_file_retrieval():
    with open('hello_world.pdf', 'rb') as file:
        content = file.read()
    try:
        file_content, _, _ = m.files.get_file_content_from_doc_id(doc_id=doc_id_list[0])
    except Exception as exc:
        assert False, str(exc)
    else:
        print(content)
        print(file_content)
        if content in file_content:
            pass
        else:
            assert False, 'File contents do not match.'


def test_annotation_retrieval():
    try:
        anns = m.annotations.get(document_id=doc_id_list[0])
        anns = json.loads(anns)[0]
    except Exception as exc:
        assert False, str(exc)
    else:
        if 'Test notes.' in anns.get('text'):
            pass
        else:
            assert False


def test_file_deletion():
    _, _, file_id = m.files.get_file_content_from_doc_id(doc_id=doc_id_list[0])
    try:
        m.files.delete(file_id=file_id)
    except Exception as exc:
        assert False, str(exc)


@nose.with_setup(teardown=cleanup)
def test_move_doc_to_trash():
    doc_id = doc_id_list.pop(0)
    try:
        m.documents.move_to_trash(doc_id=doc_id)
    except Exception as exc:
        assert False, str(exc)
    else:
        pass


if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__

    sys.path.append('database')

    result = nose.run(argv=[sys.argv[0], module_name, '-v'])



#Document Creation
#-----------------
#1) From user constructed meta
#2) From a file



#Trash testing:
#--------------
#1) Create a document