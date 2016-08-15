# -*- coding: utf-8 -*-
"""
The goal of this code is to support hosting a client library. This module
should in the end function similarly to the Mendeley Desktop.

Features:
---------
1) Initializes a representation of the documents stored in a user's library
2) Synchronizes the local library with updates that have been made remotely

"""

#Standard Library Imports
import pickle
from datetime import datetime
from timeit import default_timer as ctime
import os
import sys
import json

#Third Party Imports
import pandas as pd
from PyQt5.QtWidgets import *

# Local imports
from .api import API
from .errors import *
from . import models
from . import utils
from .optional import rr
from .optional import pdf_retrieval
from . import db_interface
# from . import archive_library

fstr = utils.float_or_none_to_string
cld = utils.get_list_class_display


class UserLibrary:
    """
    Attributes
    ----------
    api : mendeley.api.API
    user_name : string
    verbose : bool
    sync_result : Sync
    docs : Pandas DataFrame
    raw : list of json object dicts
    """

    FILE_VERSION = 1

    def __init__(self, user_name=None, verbose=False, sync=True):
        
        self.api = API(user_name=user_name,verbose=verbose)
        self.user_name = self.api.user_name
        self.verbose = verbose

        # path handling
        # -------------
        root_path = utils.get_save_root(['client_library'], True)
        save_name = utils.user_name_to_file_name(self.user_name) + '.pickle'
        self.file_path = os.path.join(root_path, save_name)

        self._load()

        if sync:
            self.sync()
        else:
            self.sync_result = None

    def __repr__(self):
        pv = ['api',        cld(self.api),
              'user_name',  self.user_name,
              'docs',       cld(self.docs),
              'raw',        cld(self.raw),
              'sync_result', cld(self.sync_result),
              'verbose',    self.verbose]
        return utils.property_values_to_string(pv)

    def sync(self,verbose=None):
        """
        Syncs the library with the Mendeley server.        
        
        Parameters
        ----------
        verbose : bool (default, inherit from class value, self.verbose)
        
        TODO:
        ? How do we know if something has been restored from the trash?
        """

        """
        Due to the complexity of syncing, the syncing code has been moved to
        its own class.
        """
        
        if verbose is None:
            verbose = self.verbose

        sync_result = Sync(self.api, self.raw, verbose=verbose)
        self.sync_result = sync_result
        self.raw = sync_result.raw
        self.docs = sync_result.docs
        self._save()

    # def archive(self):
    #     archivist = archive_library.Archivist(library=self, api=self.api)
    #     archivist.archive()

    def get_document(self, doi=None, pmid=None, index=None, return_json=False, allow_multiple=False, _check=False):
        """
        Returns the document (i.e. metadata) based on a specified identifier.
        
        Parameters
        ----------
        doi : string (default None)
        pmid : string (default None)
        index : int (default None)
            
        return_json : bool (default False)
        allow_multiple : bool (default False)
            Not yet implemented


        Returns
        -------
        models.Document object
            If return_json is False
        JSON
            If return_json is True
            
        If allow_multiple is True, then a list of results will be returned.
        """
        
        """
        TODO: We could support an indices input, that would return a list
        """        

        # TODO: Change this so that it interacts with the database, not the Pandas dataframe

        parse_rows = True

        document_json = None

        if index is not None:
            if index < 0 or index >= len(self.docs):
                if _check and index > 0:
                    return False
                else:
                    raise Exception('Out of bounds index request')
            elif _check:
                return True
                
            #For an index, we expect a single result
            document_json = [self.docs.ix[index]['json']]
            parse_rows = False

        elif doi is not None:
            #All dois in the library are stored as lower
            df_rows = self.docs[self.docs['doi'] == doi.lower()]
        elif pmid is not None:
            df_rows = self.docs[self.docs['pmid'] == pmid]
        else:
            raise Exception('get_document: Unrecognized identifier search option')


        # Handling of the parsing of the rows
        # ------------------------------------
        if parse_rows:
            # We parse rows when the rows to grab has not been specified
            # explicitly and we need to determine if we found any matches
            rows_json = df_rows['json']
            if len(rows_json) == 1:
                document_json = [rows_json[0]]
            elif len(rows_json) == 0:
                if _check:
                    return False
                else:
                    if doi is not None:
                        raise DocNotFoundError('DOI: "%s" not found in library' % doi)
                    elif pmid is not None:
                        raise DocNotFoundError('PMID: "%s" not found in library' % pmid)
                    else:
                        raise Exception('Code logic error, this should never run')
            else: 
                if allow_multiple:
                    document_json = [x for x in rows_json]
                elif _check:
                    return False
                else:
                    if doi is not None:
                        raise Exception('Multiple DOIs found for doi: "%s"' % doi)
                    elif pmid is not None:
                        raise Exception('Multiple PMIDs found for pmid: %s"' % pmid)
                    else:
                        raise Exception('Code logic error, this should never run')
              
        # Returning the results
        # ------------------------
        if _check:
            return True
        elif return_json:
            if allow_multiple:
                return document_json
            else:
                return document_json[0]
        else:
            docs = [models.Document(x, self.api) for x in document_json]
            if allow_multiple:
                return docs
            else:
                return docs[0]

    def check_for_document(self, doi=None, pmid=None):
        """
        Attempts to call self.get_document and checks for error.
        If no error, the DOI has been found.

        Parameters
        ----------
        doi - string (default None)
            Document's DOI 
        pmid - string (default None)

        Returns
        -------
        bool - True if DOI is found in the Mendeley library. False otherwise.
        """
        
        return self.get_document(doi=doi,pmid=pmid,_check=True)

    def add_to_library(self, doi=None, pmid=None, check_in_lib=False, add_pdf=True, file_path=None):
        """
        
        Parameters
        ----------
        doi : string
        check_in_lib : bool
            If true, 
        add_pdf : bool
        
        
        Improvements
        ------------
        * 
        - allow adding via PMID
        - pdf entry should be optional with default true
        - also need to handle adding pdf if possible but no error
        if not possible
        
        """
        if check_in_lib and self.check_for_document():
            raise DuplicateDocumentError('Document already exists in library.')

        #----------------------------------------------------------------------
        # Get paper information from DOI
        """
        Even then, this requires a bit of thinking. Why are we asking rr for
        paper information? Perhaps we need another repository ...
             - Pubmed
             - Crossref
             - others????

        """

        paper_info = rr.retrieve_all_info(input=doi, input_type='doi')

        # Turn the BaseEntry object into a formatted dict for submission
        # to the Mendeley API
        formatted_entry = self._format_doc_entry(paper_info.entry)

        # Create the new document
        new_document = self.api.documents.create(formatted_entry)

        """
        add_pdf
        
        * I want to be able to specify the path to the file to add.
        * Perhaps instead we want:
            pdf = file_path
            pdf = 'must_retrieve'
            pdf = 'retrieve_or_request' - If not available, make a request for it
            pdf = 'retrive_if_possible'
            
        I'm not thrilled with this specific interface, but I'd like something
        like this.
        
        We might want an additional package that focuses on retrieving pdfs.
        The big question is how to support letting these interfaces interact
        efficiently without doing things multiple times. We can answer this 
        at a later time.
        
        pdf retrieval:
            - Interlibrary loan
            - ScholarSolutions
            - PyPub
        """

        # Get pdf
        if add_pdf:
            pdf_content = pdf_retrieval.get_pdf(paper_info)
            new_document.add_file({'file' : pdf_content})

    def update_file_from_local(self, doi=None, pmid=None):
        """
        This is for updating a file in Mendeley without losing the annotations.
        The file must be saved somewhere locally, and the file path is selected by using
        a pop up file selection window.

        Parameters
        ----------
        doi - DOI of document in library to update
        pmid - PMID of document in library to update

        """
        if doi is None and pmid is None:
            raise KeyError('Please enter a DOI or PMID for the updating document.')

        document = self.get_document(doi=doi, pmid=pmid, return_json=True)
        if document is None:
            raise DOINotFoundError('Could not locate DOI in library.')

        new_file_path = self._file_selector()
        if new_file_path is None:
            return

        with open(new_file_path, 'rb') as file:
            file_content = file.read()

        doc_id = document.get('id')
        saved_annotations_string = self.api.annotations.get(document_id=doc_id)
        saved_annotations = json.loads(saved_annotations_string)

        # TODO: COME BACK TO THIS
        import pdb
        pdb.set_trace()

        has_file = document.get('file_attached')
        if has_file:
            _, _, file_id = self.api.files.get_file_content_from_doc_id(doc_id=doc_id, no_content=True)
            self.api.files.delete(file_id=file_id)

        params = {'title': document.get('title'), 'id': doc_id}
        self.api.files.link_file(file=file_content, params=params)

        # Reconfirm that the file was added
        updated = self.get_document(doi=doi, pmid=pmid, return_json=True)
        has_file = updated.get('file_attached')
        if not has_file:
            raise FileNotFoundError('File was not attached.')

        new_annotations_string = self.api.annotations.get(document_id=doc_id)
        if new_annotations_string is None or saved_annotations_string != new_annotations_string:
            self.api.annotations.create(annotation_body=saved_annotations)

    def _file_selector(self):
        app = QApplication(sys.argv)
        dialog = QFileDialog()
        # dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDirectory(os.path.expanduser('~'))
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            return filenames[0]
        else:
            return None

    def _format_doc_entry(self, entry):
        """
        Mendeley API has specific input formatting when creating a document.
         - Parses author names and separates into separate "first_name" and
            "last_name" fields.
         - Restricts keywords from being > 50 characters. If one is found,
            it is split by spaces and saved as separate keywords.
         - Changes "publication" to "publisher" to fit syntax.
         - Sets "type" to "journal"
         - Saves DOI within "identifiers" field.

        Parameters
        ----------
        entry : BaseEntry object
            See pypub.scrapers.base_objects.py
            Unformatted paper information, usually from PaperInfo class

        Returns
        -------
        entry : dict
            Paper information with proper formatting applied.
        """

        if not isinstance(entry, dict):
            entry = entry.__dict__

        # Format author names
        authors = entry.get('authors')
        formatted_author_names = None
        if authors is not None:
            if isinstance(authors[0], str):
                author_names = [x for x in authors]
            elif isinstance(authors[0], dict):
                author_names = [x.get('name') for x in authors]
            else:
                author_names = [x.name for x in authors]
            formatted_author_names = []

            # Parse author names
            for name in author_names:
                name_dict = dict()
                name = name.strip()
                parts = name.split(' ')

                # If format is "firstname middleinitial. lastname"
                if '.' in name and len(parts) == 3:
                    name_dict['first_name'] = parts[0]
                    name_dict['last_name'] = parts[2]
                # If format is "lastname, firstname"
                elif ',' in name:
                    name_dict['first_name'] = parts[1]
                    name_dict['last_name'] = parts[0]
                # If format is "lastname firstinitial"
                elif len(parts) == 2 and '.' in parts[1]:
                    name_dict['first_name'] = parts[1]
                    name_dict['last_name'] = parts[0]
                # If format is only "lastname"
                elif len(parts) == 1:
                    name_dict['last_name'] = parts[0]
                    name_dict['first_name'] = ''
                # If there are multiple initials
                elif len(parts) > 3:
                    initials = ''
                    for part in parts:
                        if '.' in part:
                            initials += part
                        else:
                            name_dict['last_name'] = part
                    name_dict['first_name'] = initials
                # Otherwise assume format is "firstname lastname" or "firstinitial. lastname"
                else:
                    name_dict['first_name'] = parts[0]
                    name_dict['last_name'] = parts[1]
                formatted_author_names.append(name_dict)

        # Make sure keywords are <= 50 characters
        kw = entry.get('keywords')
        if kw is not None:
            # Check if it's one long string, and split if so
            if isinstance(kw, str):
                kw = kw.split(', ')
            to_remove = []
            for keyword in kw:
                if len(keyword) > 50:
                    to_remove.append(keyword)
                    smaller_keywords = keyword.split(' ')
                    for word in smaller_keywords:
                        kw.append(word)
            for long_word in to_remove:
                kw.remove(long_word)
        entry['keywords'] = kw


        # Get rid of alpha characters in Volume field
        vol = entry.get('volume')
        if vol is not None:
            entry['volume'] = ''.join(c for c in vol if not c.isalpha())

        # Get rid of alpha characters in Year field
        year = entry.get('year')
        if year is not None:
            entry['year'] = ''.join(c for c in year if not c.isalpha())
            if entry['year'] == '':
                entry['year'] = None

        doi = entry.get('doi')
        if doi is not None:
            doi = doi.lower()
            entry['identifiers'] = {'doi' : doi}

        entry['authors'] = formatted_author_names
        entry['publisher'] = entry['publication']
        entry['type'] = 'journal'

        return entry

    def _load(self):
        # TODO: Check that the file is not empty ...
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'rb') as pickle_file:
                d = pickle.load(pickle_file)

            self.raw = d['raw']
            self.docs = _raw_to_data_frame(self.raw)
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
    This object should perform the syncing and include some 
    debugging information as well
    
    Attributes
    ----------
    time_deleted_check
    time_full_retrieval
    time_modified_check
    time_trash_retrieval
    time_update_sync
    
    #TODO: Update with other attributes in this class
    
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

        # Populated_values
        # -----------------
        self.deleted_ids = None
        self.trash_ids = None
        self.new_and_updated_docs = None

        if self.raw is None:
            self.full_sync()
        else:
            self.update_sync()

    def __repr__(self):
        pv = ['raw', cld(self.raw), 
            'docs', cld(self.docs),
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

        self.raw = [x.json for x in doc_set]
        self.docs = _raw_to_data_frame(self.raw)

        for entry in self.raw:
            db_interface.add_to_db(entry)

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

        # Let's work with everything as a dataframe
        self.docs = _raw_to_data_frame(self.raw)

        # Determine the document that was updated most recently. We'll ask for
        # everything that changed after that time. This avoids time sync
        # issues with the server and the local computer since everything
        # is done relative to the timestamps from the server.
        newest_modified_time = self.docs['last_modified'].max()
        self.newest_modified_time = newest_modified_time

        # The problem with the above approach is that Mendeley returns
        # documents updated since AND at 'newest_modified_time'. This
        # means that the call always returns >= 1 document.
        # Try adding a second to 'newest_modified_time'
        later_modified_time = newest_modified_time + pd.Timedelta('00:00:01')

        # Remove old ids
        #------------------------------------
        self.get_trash_ids()
        #self.get_deleted_ids(newest_modified_time)
        self.get_deleted_ids(later_modified_time)
        self.remove_old_ids()

        # Process new and updated documents
        # ------------------------------------
        updates_and_new_entries_start_time = ctime()
        self.verbose_print('Checking for modified or new documents')
        #self.get_updates_and_new_entries(newest_modified_time)
        self.get_updates_and_new_entries(later_modified_time)
        self.time_modified_processing = ctime() - updates_and_new_entries_start_time
        self.verbose_print('Done updating modified and new documents')

        self.raw = self.docs['json'].tolist()

        self.time_update_sync = ctime() - start_sync_time

        self.verbose_print('Done running "UPDATE SYNC" in %s seconds' % fstr(self.time_update_sync))

    def get_updates_and_new_entries(self, newest_modified_time):
        """        
        # 3) check modified since - add/update as necessary
        #-------------------------------------------------
        # I think for now to keep things simple we'll relate everything
        # to the newest last modified value, rather than worrying about
        # mismatches in time between the client and the server
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

        # Log the new entries in the database
        for x in range(len(new_rows_df)):
            row = new_rows_df.iloc[x]
            db_interface.add_to_db(row)

        # Log the updated entries in the database
        for x in range(len(updated_rows_df)):
            row = updated_rows_df.iloc[x]
            db_interface.update_db_entry(row)

        if len(new_rows_df) > 0:
            self.verbose_print('%d new documents found' % len(new_rows_df))
            self.docs = self.docs.append(new_rows_df)

        if len(updated_rows_df) > 0:
            self.verbose_print('%d updated documents found' % len(updated_rows_df))
            in_old_mask = updated_rows_df.index.isin(self.docs.index)
            if not in_old_mask.all():
                print('Logic error, updated entries are not in the original')
                raise Exception('Logic error, updated entries are not in the original')

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
        self.trash_ids = [x.doc_id for x in trash_set]

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
    Parameters
    ----------
    raw : json
        JSON data, generally (always?) from the Mendeley server. 
    """
    
    """
    Status: This is currently a bit of a mess because of Pandas auto-inference.
    We might also switch all of this over to a SQL database.
    Pandas also likes to use NaNs, which is nice for ignoring missing data, but
    goes against Python's typical usage of None to indicate that a value has not 
    been set. This can cause headaches in later processing.
    """    
    
    # Note that I'm not using the local attribute
    # as we can then use this for updating new information
    df = pd.DataFrame(raw)
    
    #dtype=str   => doesn't work, wtf
    #dtype={'identifiers':object}    => doesn't work, wtf
    
    #TODO: This is a complete mess with type inference ...    
    
    #TODO: The identifiers column may not exist :/ which would cause an error
    #below

    #Our goal with this line is that
    #https://github.com/pydata/pandas/issues/1972
    df['identifiers'] = df['identifiers'].where(pd.notnull(df['identifiers']),None)    
    
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
        return x.get('doi', '').lower()
    except:
        return ''

def raise_(ex):
    raise ex