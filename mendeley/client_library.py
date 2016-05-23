# -*- coding: utf-8 -*-
"""
The goal of this code is to support hosting a client library. This module
should in the end function similarly to the Mendeley Desktop.

Features:
---------
1) Initializes

TODO:
-----
1) Need to implement getting new papers and deleting old ones

"""

from datetime import datetime

from timeit import default_timer as ctime
import os
import pandas as pd
import pickle

import pdb

from .utils import float_or_none_to_string as fstr
from .utils import get_list_class_display as cld
from . import utils
from .api import API
from . import models


class UserLibrary:
    """
    Attributes
    ----------
    docs : Pandas entry
    raw : list of dicts
    raw_trash : list of dicts

    """

    FILE_VERSION = 1

    def __init__(self, user_name=None, verbose=False):
        self.api = API(user_name=user_name)
        self.user_name = self.api.user_name
        self.verbose = verbose

        # path handling
        # -------------
        root_path = utils.get_save_root(['client_library'], True)
        save_name = utils.user_name_to_file_name(self.user_name) + '.pickle'
        self.file_path = os.path.join(root_path, save_name)

        self._load()

        self.sync()

    def __repr__(self):
        pv = ['api', cld(self.api),
              'user_name', self.user_name,
              'docs', cld(self.docs),
              'raw', cld(self.raw)]
        return utils.property_values_to_string(pv)

    def sync(self):
        """
        Syncing approach:
        
        ? How do we know if something has been restored from the trash?
        
        """

        sync_result = Sync(self.api, self.raw, verbose=self.verbose)
        self.sync_result = sync_result
        self.raw = sync_result.raw
        self.docs = sync_result.docs
        self._save()

    def get_document(self, doi, return_json=False):
        """
        Returns the document (i.e. metadata) for a given DOI,
        if the DOI is found in the library.

        Parameters
        ----------
        doi : str
        return_json : bool

        Returns
        -------
        models.CreatedDocument object
            If return_json is False
        JSON
            If return_json is True

        """
        # Search through library for a document with target DOI.
        doc_id = None
        document = None
        for paper in self.raw:
            if 'identifiers' in paper.keys():
                if 'doi' in paper['identifiers'].keys():
                    if paper['identifiers']['doi'] == doi:
                        doc_id = paper['id']
                        document = paper
                        break
        if doc_id is None:
            raise KeyError("DOI not found in library")

        if return_json:
            return document
        else:
            doc_obj = models.CreatedDocument(document, API)
            return doc_obj

    def _load(self):
        # TODO: Check that the file is not empty ...
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'rb') as pickle_file:
                d = pickle.load(pickle_file)

            self.raw = d['raw']
        else:
            self.raw = None
            self.docs = None

    def _save(self):
        d = dict()
        d['file_version'] = self.FILE_VERSION
        d['raw'] = self.raw
        # d['raw_trash'] = self.raw_trash
        with open(self.file_path, 'wb') as pickle_file:
            pickle.dump(d, pickle_file)


class Sync(object):
    """
    I think this object should perform the syncing and include some 
    debugging information as well
    
    Attributes
    ----------
    time_deleted_check
    time_full_retrieval
    time_modified_check
    time_trash_retrieval
    time_update_sync
    
    """

    def __init__(self, api, raw, verbose=False):
        self.time_full_retrieval = None
        self.time_deleted_check = None
        self.time_trash_retrieval = None
        self.time_modified_check = None
        self.time_modified_processing = None
        self.newest_modified_time = None
        self.n_docs_removed = 0

        self.time_update_sync = None

        self.api = api
        self.verbose = verbose

        self.raw = raw

        #pdb.set_trace()

        # Populated_values
        # -----------------
        self.deleted_ids = None
        self.trash_ids = None
        self.new_and_updated_docs = None

        if self.raw is None:
            self.full_sync()
        else:
            self.update_sync()

        # If no documents are found, self.docs will have length 0.
        if len(self.docs) != 0:
            self.raw = self.docs['json'].tolist()

    def __repr__(self):
        pv = [
            'raw', cld(self.raw), 'docs', cld(self.docs),
            'time_full_retrieval', fstr(self.time_full_retrieval),
            'time_update_sync', fstr(self.time_update_sync),
            'newest_modified_time', self.newest_modified_time,
            'time_deleted_check', fstr(self.time_deleted_check),
            'time_trash_retrieval', fstr(self.time_trash_retrieval),
            'time_modified_check', fstr(self.time_modified_check),
            'time_modified_processing', fstr(self.time_modified_processing),
            'deleted_ids', cld(self.deleted_ids),
            'trash_ids', cld(self.trash_ids),
            'n_docs_removed', '%d' % self.n_docs_removed,
            'new_and_updated_docs', cld(self.new_and_updated_docs)]

        return utils.property_values_to_string(pv)

    def full_sync(self):

        t1 = ctime()
        self.verbose_print('Starting retrieval of all documents')

        # TODO: Change limit to -1, build in support for getting all
        # within the caller
        doc_set = self.api.documents.get(limit=500, view='all')

        #pdb.set_trace()

        self.raw = [x.json for x in doc_set]
        self.docs = _raw_to_data_frame(self.raw)

        self.full_retrieval_time = ctime() - t1

        if self.raw is not None:
            self.verbose_print('Finished retrieving all documents (n=%d) in %s seconds'
                                % (len(self.raw), fstr(self.full_retrieval_time)))
        else:
            self.verbose_print('No documents found in %s seconds'
                               % fstr(self.full_retrieval_time))

    def update_sync(self):

        self.verbose_print('Running "UPDATE SYNC"')

        start_sync_time = ctime()

        self.docs = _raw_to_data_frame(self.raw)

        newest_modified_time = self.docs['last_modified'].max()

        self.newest_modified_time = newest_modified_time

        self.get_trash_ids()

        self.get_deleted_ids(newest_modified_time)

        self.remove_old_ids()

        # -------------------------------------------------------
        updates_and_new_entries_start_time = ctime()
        self.verbose_print('Checking for modified or new documents')
        self.get_updates_and_new_entries(newest_modified_time)
        self.time_modified_processing = ctime() - updates_and_new_entries_start_time
        self.verbose_print('Done updating modified and new documents')

        self.time_update_sync = ctime() - start_sync_time

        self.verbose_print('Done running "UPDATE SYNC" in %s seconds' % fstr(self.time_update_sync))

    def get_updates_and_new_entries(self, newest_modified_time):
        """        
        #3) check modified since - add/update as necessary
        #-------------------------------------------------
        #I think for now to keep things simple we'll relate everything
        #to the newest last modified value, rather than worrying about
        #mismatches in time between the client and the server
        """

        start_modified_time = ctime()
        # TODO: Include -1 here ...
        doc_set = self.api.documents.get(modified_since=newest_modified_time, view='all')
        raw_au_docs = [x.json for x in doc_set]
        self.new_and_updated_docs = doc_set.docs
        self.time_modified_check = ctime() - start_modified_time

        if len(raw_au_docs) == 0:
            return

        # TODO: Update name, I thought this was referring to our official copy
        # which is currently self.docs
        df = _raw_to_data_frame(raw_au_docs)

        is_new_mask = df['created'] > newest_modified_time
        new_rows_df = df[is_new_mask]
        updated_rows_df = df[~is_new_mask]
        if len(new_rows_df) > 0:
            self.verbose_print('%d new documents found' % len(new_rows_df))
            self.docs = self.docs.append(new_rows_df)

        if len(updated_rows_df) > 0:
            self.verbose_print('%d updated documents found' % len(updated_rows_df))
            in_old_mask = updated_rows_df.index.isin(self.docs.index)
            if not in_old_mask.all():
                print('Logic error, updated entries are not in the original')
                import pdb
                pdb.set_trace()
                # raise Exception('Logic error, updated entries are not in the original')

            updated_indices = updated_rows_df.index
            self.docs.drop(updated_indices, inplace=True)

            self.docs = pd.concat([self.docs, updated_rows_df])

    def get_trash_ids(self):
        """
        Here we are looking for documents that have been moved to the trash.
        
        ??? Can we check the trash that's been moved back to the main
        """

        trash_start_time = ctime()
        self.verbose_print('Checking trash')

        trash_set = self.api.trash.get(limit=500, view='all')
        self.trash_ids = [x.id for x in trash_set]

        self.verbose_print('Finished checking trash, %d documents found' % len(self.trash_ids))
        self.time_trash_retrieval = ctime() - trash_start_time

    def get_deleted_ids(self, newest_modified_time):

        # 2) Check deleted
        deletion_start_time = ctime()
        self.verbose_print('Requesting deleted file IDs')

        # This is way way faster :/ than the documents.get() method although
        # it is only documented sparsly.
        # TODO: We could do the string conversion in the api
        self.deleted_ids = self.api.documents.deleted_files(since=newest_modified_time)

        self.verbose_print('Done requesting deleted file IDs, %d found' % len(self.deleted_ids))
        self.time_deleted_check = ctime() - deletion_start_time

    def remove_old_ids(self):
        # Removal of ids
        # --------------
        ids_to_remove = self.trash_ids + self.deleted_ids
        if len(ids_to_remove) > 0:
            delete_mask = self.docs.index.isin(ids_to_remove)
            keep_mask = ~delete_mask
            self.n_docs_removed = sum(delete_mask)
            self.docs = self.docs[keep_mask]

    def verbose_print(self, msg):
        if self.verbose:
            print(msg)


def _raw_to_data_frame(raw, include_json=True):
    """
    
    """
    # Note that I'm not using the local attribute
    # as we can then use this for updating new information
    df = pd.DataFrame(raw)

    # len(df) == 0 means that no documents were found.
    # Further operations on df would fail.
    if len(df) == 0:
        return df

    df.set_index('id', inplace=True)

    if include_json:
        df['json'] = raw

    # 2010-03-16T16:39:02.000Z
    # https://github.com/closeio/ciso8601
    # t2 = time.clock()
    df['created'] = df['created'].apply(parse_datetime)
    # print(time.clock() - t2)
    # strptime("2008-09-03T20:56:35.450686Z", "%Y-%m-%dT%H:%M:%S.%fZ")

    # t2 = time.clock()
    df['last_modified'] = df['last_modified'].apply(parse_datetime)
    # print(time.clock() - t2)
    df['issn'] = df['identifiers'].apply(parse_issn)
    df['pmid'] = df['identifiers'].apply(parse_pmid)
    df['doi'] = df['identifiers'].apply(parse_doi)

    return df


def parse_datetime(x):
    return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")


# def datetime_to_string(x):
#    return x.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def parse_issn(x):
    # This value is not necessarily clean
    # e.g 17517214 => 1751-7214???
    try:
        return x.get('issn', '')
    except:
        return ''


def parse_pmid(x):
    try:
        return x.get('pmid', '')
    except:
        return ''


def parse_doi(x):
    try:
        return x.get('doi', '')
    except:
        return ''
