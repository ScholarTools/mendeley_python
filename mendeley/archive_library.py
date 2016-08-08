# Standard imports
import os
import sys
import inspect
import zipfile
import math
import json

# Local imports
from mendeley import client_library
from mendeley import api


class Archivist:
    def __init__(self):
        self.library = client_library.UserLibrary()
        self.doc_list = self.library.raw

        self.m = api.API()

        self.archive_list = []
        self.volume_number = 1

        # Create paths to save the file
        self.package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        # Go up to root, then down to specific save path
        root_path = os.path.split(self.package_path)[0]
        self.save_folder_path = os.path.join(root_path, 'archives')

        if not os.path.exists(self.save_folder_path):
            os.makedirs(self.save_folder_path)

    def archive(self):

        self.current_folder = self.save_folder_path + '/volume' + str(self.volume_number)
        os.makedirs(self.current_folder)

        self.doc_length = len(self.doc_list)
        sys.stdout.write('Found %d documents in library.' % self.doc_length)

        self.progress_counter = 0
        self.progress_increment = (self.doc_length - 1) / 100
        sys.stdout.write("\r%d%%" % self.progress_counter)
        sys.stdout.flush()

        # Iterate over all documents in library
        for count, doc in enumerate(self.doc_list):

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
                except Exception as exc:
                    file_content = ''
                    file_name = 'none' + str(count) + '.pdf'
                    comment = 'Failed to get_file_content_from_doc_id at count %d' % count
                    self.log_exception(exc=exc, comment=comment, doc=doc)

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
                pdf_save_path = self.current_folder + '/' + file_name + '.pdf'
                with open(pdf_save_path, 'wb') as file:
                    file.write(file_content)

            self.archive_list.append(doc)

            # Update progress percentage
            current_progress = math.floor(count/self.progress_increment)
            if current_progress > self.progress_counter:
                self.progress_counter = current_progress
                sys.stdout.write("\r%d%%" % self.progress_counter)
                sys.stdout.flush()

        # Finally, write the last document data to a folder
        self.write_doc_data(last_iteration=True)

    def write_doc_data(self, last_iteration=False):
        # Write to the current folder
        json_file = self.current_folder + '/document_list_' + str(self.volume_number)
        with open(json_file, 'w') as file:
            file.write(json.dumps(self.archive_list))

        # Reset
        self.archive_list = []

        # Zip folder
        self.zipdir(self.current_folder, self.volume_number)

        # Make a new folder if there are more documents to save
        if not last_iteration:
            new_folder = self.save_folder_path + '/volume' + str(self.volume_number)
            os.makedirs(new_folder)
            self.volume_number += 1
            self.current_folder = new_folder

    def zipdir(self, path, volume_number):
        zip_name = 'Volume_' + str(volume_number) + '.zip'
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

        log_dict = {'Exception': exc, 'Comment': comment,
                    'Doc Title': doc_title, 'Doc DOI': doc_doi}

        logfile = self.save_folder_path + '/logfile.txt'
        with open(logfile, 'a') as file:
            file.write(json.dumps(log_dict))


a = Archivist()
a.archive()
