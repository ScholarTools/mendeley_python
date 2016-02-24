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

#I'm not sure I want to include this c dependency ...
#from ciso8601 import parse_datetime
from datetime import datetime

import time
import os
import pandas as pd
import pickle

from .utils import get_truncated_display_string as td
from .utils import get_list_class_display as cld
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
     
    def __repr__(self):
        pv = ['api',cld(self.api),
              'user_name',self.user_name,
              'docs',cld(self.docs),
                'raw',cld(self.raw)]
        return utils.property_values_to_string(pv)
    
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
            
            self.docs = self._raw_to_data_frame(self.raw)
        else:
            #Ok, with a lot of messsing around I think the full operation
            #should be:
            #1) check trash - remove documents from list
            #2) check deletd - remove documents from list
            #3) check modified since, add/update as necessary ...
        
            #I think for now to keep things simple we'll relate everything
            #to the newest last modified value, rather than worrying about
            #mismatches in time between the client and the server
            last_updated_idx = self.docs['last_modified'].idxmax()
            ts_value = self.raw[last_updated_idx]['last_modified']
            
            #1) Check trash - need API in place            
            
            #2) Check deleted
            temp = self.api.documents.get(deleted_since = ts_value)
            deleted_ids = [x.id for x in temp]
            import pdb
            pdb.set_trace()
            
            #oldest_updated_idx = df['last_modified'].idxmin(
            
            import pdb
            pdb.set_trace()
            
            #This only applies to documents that have been deleted
            #from the trash, how do we find out if documents are in the trash
            #or not?
            wtf = self.api.documents.get(deleted_since = ts_value)
            wtf2 = self.api.documents.get(modified_since = self.raw[last_updated_idx]['last_modified'])
            import pdb
            pdb.set_trace()
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

        #2010-03-16T16:39:02.000Z
        #https://github.com/closeio/ciso8601
        #t2 = time.clock()            
        df['created'] = df['created'].apply(parse_datetime)
        #print(time.clock() - t2)
        #strptime("2008-09-03T20:56:35.450686Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        #t2 = time.clock()
        df['last_modified'] = df['last_modified'].apply(parse_datetime)
        #print(time.clock() - t2)

        df['issn'] = df['identifiers'].apply(parse_issn)
        df['pmid'] = df['identifiers'].apply(parse_pmid)
        df['doi'] = df['identifiers'].apply(parse_doi)

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
        
def parse_datetime(x):
    return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")
    
def parse_issn(x):
    #This value is not necessarily clean
    #e.g 17517214 => 1751-7214???
    try:
        return x.get('issn','')
    except:
        return ''
        
def parse_pmid(x):
    try:
        return x.get('pmid','')
    except:
        return ''
        
def parse_doi(x):
    try:
        return x.get('doi','')
    except:
        return ''