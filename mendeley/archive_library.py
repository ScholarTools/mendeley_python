# Standard imports
import os
import sys
import inspect
import zipfile
import math
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Local imports
from mendeley import client_library
from mendeley import api


class Archivist:
    def __init__(self, library=None, entered_api=None):
        if library is None:
            self.library = client_library.UserLibrary()
        else:
            self.library = library

        self.doc_list = self.library.raw

        if entered_api is None:
            self.m = api.API()
        else:
            self.m = entered_api

        self.archive_list = []
        self.volume_number = 1
        self.retry_counter = 0

    def archive(self, root_path=None):
        # Setup
        # -----

        # Create paths to save the file
        if root_path is None:
            self.root_path = self.file_selector()
        else:
            self.root_path = root_path

        # Go up to root, then down to specific save path
        self.save_folder_path = os.path.join(self.root_path, 'archives')

        self.downloaded_papers = []
        self.downloaded_paper_file = os.path.join(self.save_folder_path, 'downloaded_paper_titles.txt')

        # Check to see if archive has been run before and saved files already exist
        if not os.path.exists(self.save_folder_path):
            os.makedirs(self.save_folder_path)
        else:
            if os.path.isfile(self.downloaded_paper_file):
                with open(self.downloaded_paper_file, 'r') as file:
                    for line in file:
                        stripped = line.replace('\n', '')
                        self.downloaded_papers.append(stripped)

            # If volumes of saved data exist, move the number up to not overwrite data
            dir_volume = os.path.join(self.save_folder_path, ('volume' + str(self.volume_number)))
            while os.path.exists(dir_volume):
                self.volume_number += 1
                dir_volume = os.path.join(self.save_folder_path, ('volume' + str(self.volume_number)))

        self.current_folder = os.path.join(self.save_folder_path, ('volume' + str(self.volume_number)))
        os.makedirs(self.current_folder)

        self.doc_length = len(self.doc_list)
        sys.stdout.write('Found %d documents in library.' % self.doc_length)

        file_counter = 0

        self.progress_counter = 0
        self.progress_increment = (self.doc_length - 1) / 100
        sys.stdout.write("\r%d%%" % self.progress_counter)
        sys.stdout.flush()

        # Iteration
        # ---------

        # Iterate over all documents in library
        for count, doc in enumerate(self.doc_list):

            if doc.get('title') in self.downloaded_papers:
                continue

            # Divide the library archives into multiple folders, each with 100 papers
            if count > 0 and count%100 == 0:
                try:
                    self.write_doc_data()
                except Exception as exc:
                    comment = 'Failed to write_doc_data() at count %d' % count
                    self.log_exception(exc=exc, comment=comment, doc=doc)

            # Check for/retrieve and set notes
            notes = doc.get('notes')
            if notes is None:
                notes = ''
            doc['notes'] = notes

            # Check if the document has a file
            has_file = doc.get('file_attached')
            if has_file:
                doc_id = doc.get('id')

                # First get the content and name of the attached pdf
                try:
                    file_content, file_name = self.m.files.get_file_content_from_doc_id(doc_id=doc_id)
                except PermissionError:
                    self.retry_counter += 1
                    if self.retry_counter <= 5:
                        # If a server error was encountered, retry (maximum of 5 times)
                        self.archive(root_path=self.root_path)
                    else:
                        raise ConnectionError('PermissionError encountered and 5 archival retries failed.')
                except Exception as exc:
                    file_content = ''
                    file_name = 'none' + str(count)
                    comment = 'Failed to get_file_content_from_doc_id at count %d' % count
                    self.log_exception(exc=exc, comment=comment, doc=doc)

                if '.pdf' not in file_name:
                    file_name += '.pdf'

                # Next get the annotations, if any
                try:
                    annotations = self.m.annotations.get(document_id=doc_id)
                except Exception as exc:
                    annotations = None
                    comment = 'Failed to retrieve annotations at count %d' % count
                    self.log_exception(exc=exc, comment=comment, doc=doc)

                # Add to dict
                doc['file_name'] = file_name
                doc['annotations'] = annotations

                # Write pdf to disk
                pdf_save_path = os.path.join(self.current_folder, file_name)
                with open(pdf_save_path, 'wb') as file:
                    file.write(file_content)

            self.archive_list.append(doc)

            # Record that the file was downloaded.
            file_counter += 1
            with open(self.downloaded_paper_file, 'a') as file:
                file.write(doc.get('title') + '\n')

            # Update progress percentage
            current_progress = math.floor(count/self.progress_increment)
            if current_progress > self.progress_counter:
                self.progress_counter = current_progress
                sys.stdout.write("\r%d%%" % self.progress_counter)
                sys.stdout.flush()

        # Write the last document data to a folder
        self.write_doc_data(last_iteration=True)

        # Finally, zip everything
        root_save_path = os.path.join(self.root_path, 'Archived_Library.zip')
        self.zipdir(self.save_folder_path, root_save_path)

    def write_doc_data(self, last_iteration=False):
        # Write to the current folder
        json_file = os.path.join(self.current_folder, ('document_list_' + str(self.volume_number)))
        with open(json_file, 'w') as file:
            file.write(json.dumps(self.archive_list))

        # Reset
        self.archive_list = []

        # Make a new folder if there are more documents to save
        if not last_iteration:
            new_folder = os.path.join(self.save_folder_path, ('volume' + str(self.volume_number)))
            os.makedirs(new_folder)
            self.volume_number += 1
            self.current_folder = new_folder

    def zipdir(self, path, zip_name):
        zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(path):
            for file in files:
                zipf.write(os.path.join(root, file))

        zipf.close()

    def log_exception(self, exc, comment, doc):
        # For recording exceptions that arise while archiving
        doc_title = doc.get('title')
        if doc_title is None:
            doc_title = ''

        ids = doc.get('identifiers')
        if ids is not None:
            doc_doi = ids.get('doi')
        else:
            doc_doi = None

        if isinstance(exc, PermissionError):
            exc = 'PermissionError: Could not connect to server.'

        log_dict = {'Exception': exc, 'Comment': comment,
                    'Doc Title': doc_title, 'Doc DOI': doc_doi}

        logfile = os.path.join(self.save_folder_path, 'logfile.txt')
        with open(logfile, 'a') as file:
            file.write(json.dumps(log_dict))

    def file_selector(self):
        app = QApplication(sys.argv)
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDirectory(os.path.expanduser('~'))
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            return filenames[0]
        else:
            return os.path.expanduser('~')

a = Archivist()
a.archive()
