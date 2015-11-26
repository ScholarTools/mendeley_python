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


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import os

from . import utils
from . import api as mapi

"""
Testing Code:

from mendeley import client_library

temp = client_library.UserLibrary()

temp.syncIDs()

"""
Base = declarative_base()

class LibraryEntryId(Base):
    __tablename__ = 'library_entry_id'

    #??? - we also have an id from Mendeley
    id = Column(Integer, primary_key=True)    
    doc_id = Column(String(15))
    doc_version = Column(Integer) #I think this is a date ...

class LibraryEntry(Base):
    __tablename__ = 'library_entry'
    
    id = Column(Integer, primary_key=True)     
    
    title = Column(String)
    journal = Column(String)
    pmid = Column(String)    
    """
    entry_type
    year
    volume
    doi
    pmid
    """    
    
class UserLibrary():
    
    def __init__(self, user_name=None):
        self.um = mapi.UserMethods(user_name=user_name)
        
        #Initialize DB Connection
        db_root = utils.get_save_root('databases')
        db_name = utils.user_name_to_file_name(self.um.user_name) + '.db'
        db_path = os.path.join(db_root,db_name)
        
        sqlite_db_path = 'sqlite:///' + db_path

        self.db_path = sqlite_db_path      
        
        engine = create_engine(sqlite_db_path)
        
        if not os.path.isfile(sqlite_db_path):
            Base.metadata.create_all(engine)             
        
        
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def commit(self):
        self.session.commit()

    def syncIDs(self):
        #??? How would I get the last sync date????
        #Perhaps just query the table
        #temp = 
    
        temp = self.um.docs_get_library_ids(get_all=True)
        import pdb
        pdb.set_trace()

    def sync(self):
        pass
    
    
    