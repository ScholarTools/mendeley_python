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

from timeit import default_timer as ctime
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
    raw_trash : list of dicts
    
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
        """
        Syncing approach:
        
        ? How do we know if something has been restored from the trash?
        
        """

        #TODO:
        #sync_result = Sync(self.raw)
        #unpack result
        
        if self.raw is None:
            #Get it all
            t1 = time.clock()
            print('Starting retrieval')
            doc_set = self.api.documents.get(limit=500,view='all')
            self.raw = [x.json for x in doc_set]
            trash_set = self.api.trash.get(limit=500,view='all')
            self.raw_trash = [x.json for x in trash_set]
            print(time.clock() - t1)
            
            
            t2 = time.clock()
            self._save()
            print(time.clock() - t2)
            
            self.docs = self._raw_to_data_frame(self.raw)
        else:
            t2 = ctime()
            #Ok, with a lot of messsing around I think the full operation
            #should be:
            #1) check trash - remove documents from list
            #2) check deletd - remove documents from list
            #3) check modified since, add/update as necessary ...
            last_updated_idx = self.docs['last_modified'].idxmax()
            newest_modified_time = self.docs.ix[last_updated_idx,'last_modified']
            #NOTE: We could just convert the time back to a string ...
            numeric_idx = self.docs.index.get_loc(last_updated_idx)
            newest_modified_time_str = self.raw[numeric_idx]['last_modified']  

            
            #1) Check trash - need API in place     
            #Can we check for trash that's been moved back
            #to the main 
            t1 = ctime()
            print('trash check')
            trash_set = self.api.trash.get(limit=500,view='all')
            trash_ids = [x.id for x in trash_set]  
            print(ctime() - t1)
            
            #raw_trash = [x.json for x in trash_set]
            #trash_ids = [x['id'] for x in raw_trash]            
                     
            #2) Check deleted
            t1 = ctime()
            print('Deleted check')
            #This is way way faster :/
            deleted_ids = self.api.documents.deleted_files(since = newest_modified_time_str)
            #deleted_ids = [x['id'] for x in temp]
            #temp = self.api.documents.get(deleted_since = newest_modified_time_str)
            #deleted_ids = [x.id for x in temp]
            print(ctime() - t1)

            #Removal of ids
            #--------------
            ids_to_remove = trash_ids + deleted_ids
            if len(ids_to_remove) > 0:
                delete_mask = self.docs.index.isin(ids_to_remove)
                keep_mask = ~delete_mask
                self.docs = self.docs[keep_mask]
                self.raw = [x for x,y in zip(self.raw,keep_mask) if y]
            
            #3) check modified since - add/update as necessary
            #-------------------------------------------------
            #I think for now to keep things simple we'll relate everything
            #to the newest last modified value, rather than worrying about
            #mismatches in time between the client and the server
                 
            t1 = ctime()
            print('Modified check')
            doc_set = self.api.documents.get(modified_since = newest_modified_time_str)
            raw_au_docs = [x.json for x in doc_set]
            print(ctime() - t1)
                       
            
            if len(raw_au_docs) > 0:
                df = self._raw_to_data_frame(raw_au_docs)
                is_new_mask = df['created'] > newest_modified_time
                new_rows_df = df[is_new_mask]
                new_raw = [x for x,y in zip(raw_au_docs,is_new_mask) if y]
                updated_rows_df = df[~is_new_mask]
                updated_raw = [x for x,y in zip(raw_au_docs,is_new_mask) if not y]
                if len(new_rows_df) > 0:
                    #TODO: Merge old with new
                    print('New values discovered, need to update this code')
                    import pdb
                    pdb.set_trace()
                    
                if len(updated_rows_df) > 0:
                    in_old_mask = updated_rows_df.index.isin(self.docs.index)
                    if not in_old_mask.all():
                        print('Logic error, updated entries are not in the original')
                        import pdb
                        pdb.set_trace()
                        #raise Exception('Logic error, updated entries are not in the original')
                        
                    
                    #This approach is not great and could likely be improved ...
                    #We're running into issues because of needing to align by
                    #the list. We might need to switch to a dict ...
                    for index, cur_new_entry in updated_rows_df.iterrows():
                        row_in_master = self.docs.index.get_loc(index)
                        #I = self.docs.index.get_loc
                        #- find location in dataframe
                        #- find location in rows
                        del self.raw[row_in_master]
                        self.docs.drop(index,inplace=True)
                    
                    self.raw = self.raw + updated_raw
                    self.docs = pd.concat([self.docs,updated_rows_df])
                    
                    print(ctime() - t2) 
            

    def get_document_objects(self,doc_row_entries):
        #TODO: Resolve from df rows to raw, then call
        #constructor in models
        import pdb
        pdb.set_trace()
        pass



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
        #d['raw_trash'] = self.raw_trash
        with open(self.file_path, 'wb') as pickle_file:
            pickle.dump(d,pickle_file)
        
        
class Sync(object):
    
    """
    I think this object should perform the syncing and include some 
    debugging information as well
    
    Parameters
    ----------
    
    
    """
    def __init__(self,api,raw,verbose=False):
        
        self.api = api
        self.verbose = verbose
        self.full_retrieval_time = None
        self.trash_retrieval_time = None
        
        #Outputs
        #------------------
        self.raw = raw

        if self.raw is None:
            self.full_sync(raw)
        else:
            self.update_sync()
                
    def full_sync(self):
    
        t1 = ctime()
        self.verbose_print('Starting retrieval of all documents')
        
        #TODO: Change limit to -1, build in support for getting all
        #within the caller
        doc_set = self.api.documents.get(limit=500,view='all')
        
        #TODO: make this a dict
        self.raw = [x.json for x in doc_set]
        self.full_retrieval_time = ctime() - t1
        
        self.verbose_printf('Finished retrieving all documents (n=%d) in %0.2f seconds' 
            % (len(self.raw),self.full_retrieval_time))
                
    def verbose_print(self,msg):
        if self.verbose:
            print(msg) 

def _raw_to_data_frame(self,raw):
    """
    
    """
    #Note that I'm not using the local attribute
    #as we can then use this for updating new information
    df = pd.DataFrame(raw)
    df.set_index('id', inplace=True)

    if len(raw) == 0:
        return df

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