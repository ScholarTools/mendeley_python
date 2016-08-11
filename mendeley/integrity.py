# Standard imports
import concurrent.futures
from urllib.parse import quote as urllib_quote

# Third party imports
import requests

# Local imports
from database.db_errors import *
import database.db_tables as tables
from database import Session
from . import db_interface as db
from sqlalchemy import func


class Analysis(object):
    def __init__(self, library):
        self.library = library
        self.session = Session()
        self.total_paper_count = self.session.query(tables.MainPaperInfo).count()

        self.without_dois = None
        self.without_dois_count = None
        self.without_pmids = None
        self.without_pmids_count = None
        self.without_files = None
        self.without_files_count = None
        self.without_file_info = None
        self.without_file_info_count = None
        self.duplicate_doi_dict = None
        self.duplicate_entries = None


        if self.total_paper_count == 0:
            raise LookupError('No documents found in database. Please sync with library '
                              'or add documents before performing analysis.')

        self.without_dois_count = self.missing_doi_search()
        self.without_pmids_count = self.missing_pmid_search()
        (self.without_files_count, self.without_file_info_count) = self.missing_file_search()
        self.duplicate_doi_count = self.duplicate_doi_search()
        #self.invalid_doi_count = self.validate_DOIs()

    def missing_doi_search(self):
        without_dois = self.session.query(tables.MainPaperInfo).filter((tables.MainPaperInfo.in_lib == 1)
                                                                    & ((tables.MainPaperInfo.doi == None)
                                                                    | (tables.MainPaperInfo.doi == ''))).all()
        self.without_dois = without_dois

        without_dois_count = len(without_dois)
        return without_dois_count

    def missing_pmid_search(self):
        without_pmids = self.session.query(tables.MainPaperInfo).filter((tables.MainPaperInfo.pubmed_id == None)
                                                                        | (tables.MainPaperInfo.pubmed_id == '')).all()
        self.without_pmids = without_pmids

        without_pmids_count = len(without_pmids)
        return without_pmids_count

    def missing_file_search(self):
        # Documents where the has_file entry has been explicitly set to 0
        without_files = self.session.query(tables.MainPaperInfo).filter_by(has_file=0).all()
        without_files_count = len(without_files)

        self.without_files = without_files

        # Documents where the has_file entry has not been set
        without_file_info = self.session.query(tables.MainPaperInfo).filter_by(has_file=None).all()
        without_file_info_count = len(without_file_info)

        self.without_file_info = without_file_info

        return without_files_count, without_file_info_count

    def duplicate_doi_search(self):
        all_duplicates = self.session.query(tables.MainPaperInfo).\
            having(func.count(tables.MainPaperInfo.doi) > 1).\
            group_by(tables.MainPaperInfo.doi).all()

        doi_dict = {}
        # Create a dict matching DOIs to titles
        for entry in all_duplicates:
            doi = entry.doi
            if doi in doi_dict.keys():
                if isinstance(doi_dict[doi], list):
                    doi_dict[doi].append(entry.title)
                else:
                    new_list = [doi_dict[doi], entry.title]
                    doi_dict[doi] = new_list
            else:
                doi_dict[entry.doi] = entry.title

        self.duplicate_doi_dict = doi_dict
        self.duplicate_entries = all_duplicates

        return len(doi_dict.keys())

    def validate_dois(self):
        docs_with_dois = self.session.query(tables.MainPaperInfo).filter((tables.MainPaperInfo.in_lib == 1)
                                                                    & (tables.MainPaperInfo.doi != None)
                                                                    & (tables.MainPaperInfo.doi != '')).all()
        '''
        # TODO: Well, this doesn't work.
        # Use multithreading to check multiple DOIs at once
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as e:
            e.map(self._doi_validate_helper, docs_with_dois)
        '''

        # TODO: FIGURE OUT WHY SO MANY REQUESTS ARE RETURNING 404
        # Maybe it's not handling redirects properly?

        for doc in docs_with_dois:
            self._doi_validate_helper(doc)

        # Update session with changes
        self.session.commit()

        invalid_doi_count = self.session.query(tables.MainPaperInfo).filter((tables.MainPaperInfo.in_lib == 1)
                                                                    & (tables.MainPaperInfo.valid_doi == 0)).count()

        print('')
        return invalid_doi_count

    def _doi_validate_helper(self, db_object):
        doi = db_object.doi
        url = 'http://dx.doi.org/' + urllib_quote(doi)
        resp = requests.get(url)
        print(resp.status_code)
        print('Entered URL: ' + url)
        print('Response URL: ' + resp.url)
        print()
        if resp.ok:
            db_object.valid_doi = 1
        else:
            db_object.valid_doi = 0

    def __repr__(self):
        return u'' \
            'Total document count: %d\n' % self.total_paper_count + \
            'Documents without DOIs: %d\n' % self.without_dois_count + \
            'Documents without PMIDs: %d\n' % self.without_pmids_count + \
            'Documents without files: %d\n' % self.without_files_count + \
            'Documents that may be missing files: %d\n' % self.without_file_info_count + \
            'DOIs that are duplicated: %d\n' % self.duplicate_doi_count + \
            'Invalid DOIs: For number of invalid DOIs, run the Analysis.validate_DOIs method.'
