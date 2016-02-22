# -*- coding: utf-8 -*-
"""
The goal of this code is to support hosting a client library. This module
should in the end function similarly to the Mendeley Desktop.

Tasks:
- sync documents
- add entries
- expose the library with queries

Documentation for SQLAlchemy:
http://docs.sqlalchemy.org/en/rel_0_9/index.html

Examples of others:
-------------------
https://github.com/Mendeley/mendeley-oapi-example/blob/master/mendeley_client.py
https://github.com/Mendeley/mendeley-oapi-example/blob/master/synced_client.py
https://github.com/Mendeley/mendeley-api-python-example/blob/master/mendeley-example.py

"""

#TODO: How to close the db when the object is removed from memory???

import os

from . import utils
from . import API

"""
Testing Code:

from mendeley import client_library

temp = client_library.UserLibrary()

temp.syncIDs()

""" 
    
class UserLibrary():
    
    def __init__(self, user_name=None):
        self.api = API(user_name=user_name)
        
        import pdb
        pdb.set_trace()    
    