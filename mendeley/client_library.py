# -*- coding: utf-8 -*-
"""
The goal of this code is to support hosting a client library. This module
should in the end function similarly to the Mendeley Desktop.

Features:
---------
1) Initializes

TODO:
-----
1) Need to implment getting new papers and deleting old ones

"""

import time
import os
import pandas as pd
import pickle

from . import utils
from .api import API

"""
Testing Code:

from mendeley import client_library

temp = client_library.UserLibrary()

temp.syncIDs()

""" 
    
class UserLibrary():
    
    """
    Attributes
    ----------
    docs : Pandas entry
    raw : list of dicts
    
    """

    FILE_VERSION = 1    
    
    def __init__(self, user_name=None):
        self.api = API(user_name=user_name)
        self.user_name = self.api.user_name        
        
        #path handling
        #-------------
        root_path = utils.get_save_root(['client_library'],True)
        save_name = utils.user_name_to_file_name(self.user_name) + '.pickle'
        self.file_path = os.path.join(root_path,save_name)
        
                     
        self._load()
        
        self.sync()
        
    def sync(self):
        if self.raw is None:
            #Get it all
            t1 = time.clock()
            print('Starting retrieval')
            doc_set = self.api.documents.get(limit=500,view='all')
            self.raw = [x.json for x in doc_set]
            print(time.clock() - t1)
            t2 = time.clock()
            self._save()
            print(time.clock() - t2)
            
            self.docs = self._raw_to_data_frame(raw)
        else:
            #TODO:
            #1) Find newest file, anything since then?
            #2) any deletes?
            pass

    def get_document_objects(self,doc_row_entries):
        #TODO: Resolve from df rows to raw, then call
        #constructor in models
        pass

    def _raw_to_data_frame(self,raw):
        """
        
        """
        #Note that I'm not using the local attribute
        #as we can then use this for updating new information
        df = pd.DataFrame(raw)

        #Changes:
        #last_modified
        #created
        #? authors????

        return df

    def _load(self):
        #TODO: Check that the file is not empty ...
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'rb') as pickle_file:
                d = pickle.load(pickle_file)
            
            self.raw = d['raw']
            self.docs = self._raw_to_data_frame(d['raw'])
        else:
            self.raw = None
    
    def _save(self):
        d = {}
        d['file_version'] = self.FILE_VERSION
        d['raw'] = self.raw
        with open(self.file_path, 'wb') as pickle_file:
            pickle.dump(d,pickle_file)
        
    