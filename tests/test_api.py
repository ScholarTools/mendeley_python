# -*- coding: utf-8 -*-
"""
"""
from mendeley import API

m = API('testing')


def test_annotations():
    
    pass


def test_documents():
    
    temp = m.documents.create({"title": "Motor Planning", "type": "journal", "identifiers": {"doi": "10.1177/1073858414541484"}})
    
    doc_set = m.documents.get(verbose=True)

    

#Document Creation
#-----------------
#1) From user constructed meta
#2) From a file



#Trash testing:
#--------------
#1) Create a document