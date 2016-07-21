# -*- coding: utf-8 -*-
"""
This module is meant to implement all functions described at:

    #1) http://dev.mendeley.com/methods/
    #
    #   Shows request parameters a bit more clearly    
    
    #2) https://api.mendeley.com/apidocs/
    #
    #   Testing interface, nicer organization
    

General Usage
-------------
from mendeley import API
user_api = API()
public_api = API()


Request Options
---------------
In addition to the options of a given function, the following options are also
supported:

    TODO: fill this in: example _return_type

TODO: Create an options class that can be given to the request (e.g. for return type)

Method Types (from Mendeley)
----------------------------
Annotations
Academic Statuses
Catalog Documents
Catalog Search
Datasets
Disciplines
Documents
Documents Metadata Lookup
Files
File Content
Folders
Groups
Identifier Types
Locations
Profiles
Trash
Errors

"""

#Standard Library
import sys
import mimetypes
from os.path import basename
from datetime import datetime
import json

#Third party
import requests

#Local Imports
from . import auth
from . import models
from . import utils

#TODO: I'd like to switch to importing specific errors ...
from .errors import *

PY2 = int(sys.version[0]) == 2

if PY2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

BASE_URL = 'https://api.mendeley.com'

# For each view, specify which object type should be returned
catalog_fcns = {None: models.CatalogDocument,
                'bib': models.BibCatalogDocument,
                'stats': models.StatsCatalogDocument,
                'client': models.ClientCatalogDocument,
                'all': models.AllCatalogDocument
                }

document_fcns = {None: models.Document,
                 'bib': models.BibDocument,
                 'client': models.ClientDocument,
                 'tags': models.TagsDocument,
                 'patent': models.PatentDocument,
                 'all': models.AllDocument,
                 'deleted': models.DeletedDocument
                 }

#==============================================================================
class API(object):
    """
    
    Attributes
    ----------
    default_return_type : {'object','json','raw','response'}
        This is the default type to return from methods.
    verbose : bool (default False)
        
    last_response : 
    last_params : 
        
    """

    def __init__(self, user_name=None, verbose=False):
        """
        Parameters
        ----------
        user_name : string (default None)
            - None : then the default user is loaded via config.DefaultUser
            - 'public' : then the public API is accessed
        
        """

        self.verbose=verbose

        self.s = requests.Session()
        if user_name == 'public':
            self.public_only = True
            token = auth.retrieve_public_authorization()
            self.user_name = 'public'
        else:
            self.public_only = False
            token = auth.retrieve_user_authorization(user_name, session=self.s)
            self.user_name = token.user_name

        # Options ... (I might change this ...)
        self.default_return_type = 'object'

        self.access_token = token
        self.last_response = None
        self.last_params = None

        #TODO: Eventually I'd like to trim this based on user vs public
        self.annotations = Annotations(self)
        self.definitions = Definitions(self)
        self.documents = Documents(self)
        self.folders = Folders(self)
        self.files = Files(self)
        self.trash = Trash(self)

    def __repr__(self):
        # TODO: Finish all of these ..
        pv = ['public_only', self.public_only, 'user_name', self.user_name]
        return utils.property_values_to_string(pv)

    def make_post_request(self, url, object_fh, params, response_params=None, headers=None, files=None):

        #
        # http://docs.python-requests.org/en/latest/user/advanced/#streaming-uploads

        if params is not None:
            return_type = params.pop('_return_type', self.default_return_type)
        else:
            return_type = self.default_return_type

        if files is None:
            params = json.dumps(params)

        r = self.s.post(url, data=params, auth=self.access_token, headers=headers, files=files)

        if not r.ok:
            # if r.status_code != good_status:
            print(r.text)
            print('')
            # TODO: This should be improved
            raise CallFailedException('Call failed with status: %d' % (r.status_code))

        return self.handle_return(r, return_type, response_params, object_fh)

    def make_get_request(self, url, object_fh, params, response_params=None, headers=None):
        """

        Parameters:
        -----------          
        url : str
            URL to make request from.
        object_fh: function handle

        params : dict (default {})
            Dictionary of parameters to place in the GET query. Values may be
            numbers or strings.
        good_status : int (default 200)
            The status to check for as to whether or not the request 
            was successful.
        return_type : {'object','json','raw','response'}
            object - indicates that the result class object should be created.
                This is the slowest option but provides the most functionality.
            json   - 
            
        See Also:
        ---------
        .auth.UserCredentials.__call__()
        .auth.PublicCredentials.__call__()
        """

        # TODO: extract good_status = 200, return_type = None from params

        if params is None:
            params = {}
        else:
            if PY2:
                params = dict((k, v) for k, v in params.iteritems() if v)
            else:
                params = dict((k, v) for k, v in params.items() if v)

        return_type = params.pop('_return_type', self.default_return_type)

        # This was newly introduced, apparently? Each dev token is only good for 90 days
        # https://development-tokens.mendeley.com/
        dev_token = utils.dev_token

        if headers is None:
            headers = {'Development-Token' : dev_token}
        else:
            headers['Development-Token'] = dev_token

        # NOTE: We make authorization go through the access token. The request
        # will call the access_token prior to sending the request. Specifically
        # the __call__ method is called.
        resp = self.s.get(url, params=params, auth=self.access_token, headers=headers)

        #if 'annotation' in url:
        #    import pdb
        #    pdb.set_trace()

        self.last_url = url
        self.last_response = resp
        self.last_params = params

        if not resp.ok:
            # if r.status_code != good_status:
            print(resp.text)
            print('')
            # TODO: This should be improved
            raise Exception('Call failed with status: %d' % (resp.status_code))

        return self.handle_return(resp, return_type, response_params, object_fh)

    def make_patch_request(self, url, object_fh, params, response_params=None, headers=None, files=None):
        #
        # http://docs.python-requests.org/en/latest/user/advanced/#streaming-uploads

        if params is not None:
            return_type = params.pop('_return_type', self.default_return_type)
        else:
            return_type = self.default_return_type

        if files is None:
            params = json.dumps(params)

        resp = self.s.patch(url, data=params, auth=self.access_token, headers=headers, files=files)

        if not resp.ok:
            # if r.status_code != good_status:
            print(resp.text)
            print('')
            # TODO: This should be improved
            raise Exception('Call failed with status: %d' % (resp.status_code))

        return self.handle_return(resp, return_type, response_params, object_fh)

    def handle_return(self, req, return_type, response_params, object_fh):
        if return_type is 'object':
            if response_params is None:
                return object_fh(req.json(), self)
            else:
                return object_fh(req.json(), self, response_params)
        elif return_type is 'json':
            return req.json()
        elif return_type is 'raw':
            return req.text
        elif return_type is 'response':
            return req
        else:
            raise Exception('No match found for return type')

    def catalog(self, **kwargs):

        """
        
        TODO: This should probably be moved ...        
        
        Parameters
        ----------
        arxiv
        doi
        isbn
        issn
        pmid
        scopus
        filehash
        view
         - bib
         - stats
         - client - this option doesn't make much sense
         - all
        id : string
            Short for Catalog ID. Mendeley's catalog id. The only way I know of
            getting this is from a previous Mendeley search.
        
        Examples
        --------
        from mendeley import API
        m = API()
        c = m.catalog(pmid='11826063')
        c = m.catalog(pmid='11826063',view='bib')
        c = m.catalog(cid='f631d7ed-9926-34ed-b56e-0f5bb236b87b')
        """

        """
        Internal Note: Returns a list of catalog entries that match a 
        given query 
        #TODO: Is this the case for a given id? NO - only returns signle entry
        #TODO: Build this into tests
        """

        url = BASE_URL + '/catalog'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        view = kwargs.get('view')
        response_params = {'fcn': catalog_fcns[view]}

        return self.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

class Annotations(object):
    
    def __init__(self, parent):
        self.parent = parent

    def get(self, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/annotations/getAnnotations
        """

        url = BASE_URL + '/annotations'

        document_id = kwargs.get('document_id')
        if document_id is None:
            raise LookupError('Must enter a document ID to retrieve annotations.')

        #TODO: Why is kwargs not being used?
        params = dict()
        params['document_id'] = document_id
        params['include_trashed'] = False

        headers = {'Content-Type' : 'application/vnd.mendeley-annotation.1+json'}

        return self.parent.make_get_request(url, models.Annotation, params, headers=headers)

    def create(self, **kwargs):
        """
        https://api.mendeley.com/apidocs/docs#!/annotations/createAnnotation
        """
        pass

    def delete(self, **kwargs):
        url = BASE_URL + '/annotations'


        headers = {'Content-Type' : 'application/vnd.mendeley-folder.1+json'}
        pass

class Definitions(object):
    """
    TODO: These values should presumably only be queried once ...
    """

    def __init__(self, parent):
        self.parent = parent

    def academic_statuses(self, **kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/academic_statuses/get
        
        Example
        -------        
        from mendeley import API
        m = API()
        a_status = m.definitions.academic_statuses()
        """
        url = BASE_URL + '/academic_statuses'

        return self.parent.make_get_request(url, models.academic_statuses, kwargs)

    def subject_areas(self, **kwargs):
        """
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.disciplines()
        """
        url = BASE_URL + '/subject_areas'

        return self.parent.make_get_request(url, models.subject_areas, kwargs)

    def document_types(self, **kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/document_types/getAllDocumentTypes
        
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.document_types()
        """
        url = BASE_URL + '/document_types'

        return self.parent.make_get_request(url, models.document_types, kwargs)

class Documents(object):
    def __init__(self, parent):
        self.parent = parent

    def get(self, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/getDocuments
        
        Parameters
        ----------
        id : 
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string or datetime
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        deleted_since : string or datetime
            Returns only documents deleted since this timestamp. Should be 
            supplied in ISO 8601 format.
        profile_id : string
            The id of the profile that the document belongs to, that does not 
            belong to any group. If not supplied returns users documents.
        authored :
            TODO
        starred : 
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order            
        view : 
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'

        Examples
        --------
        from mendeley import API
        m = API()
        d = m.documents.get(limit=1)
        
        """

        url = BASE_URL + '/documents'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id
            
        

        convert_datetime_to_string(kwargs, 'modified_since')
        convert_datetime_to_string(kwargs, 'deleted_since')

        view = kwargs.get('view')

        if 'deleted_since' in kwargs:
            view = 'deleted'

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit, 'page_id':0}

        verbose = _process_verbose(self.parent,kwargs,response_params)
        if verbose:
            print("Requesting up to %d documents from Mendeley with params: %s" % (limit, kwargs))

        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

    def get_single(self, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/getDocuments

        Parameters
        ----------
        id :
        group_id : string
            The id of the group that the document belongs to. If not supplied
            returns users documents.
        modified_since : string or datetime
            Returns only documents modified since this timestamp. Should be
            supplied in ISO 8601 format.
        deleted_since : string or datetime
            Returns only documents deleted since this timestamp. Should be
            supplied in ISO 8601 format.
        profile_id : string
            The id of the profile that the document belongs to, that does not
            belong to any group. If not supplied returns users documents.
        authored :
            TODO
        starred :
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order
        view :
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'

        Examples
        --------
        from mendeley import API
        m = API()
        d = m.documents.get(limit=1)

        """

        url = BASE_URL + '/documents'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        convert_datetime_to_string(kwargs, 'modified_since')
        convert_datetime_to_string(kwargs, 'deleted_since')

        view = kwargs.get('view')

        if 'deleted_since' in kwargs:
            view = 'deleted'

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit}

        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

    def deleted_files(self, **kwargs):
        """
        Parameters
        ----------
        since
        group_id
        
        
        """
        convert_datetime_to_string(kwargs, 'since')

        url = BASE_URL + '/deleted_documents'
        return self.parent.make_get_request(url, models.deleted_document_ids, kwargs)

    def create(self, doc_data, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/createDocument

        Parameters
        ----------
        doc_data : dict
            'title' and 'type' fields are required. Example types include:
            'journal' and 'book'. All types can be found at:
                api.definitions.document_types()
            
        TODO: Let's create a better interface for creating these values        
        
        Example
        -------
        m = API()
        data = {"title": "Motor Planning", "type": "journal", "identifiers": {"doi": "10.1177/1073858414541484"}}
        new_doc = m.documents.create(data)
        """

        

        url = BASE_URL + '/documents'

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        verbose = _process_verbose(self.parent,kwargs,None)
        
        if verbose:
            pass


        return self.parent.make_post_request(url, models.Document, doc_data, headers=headers)


    def create_from_file(self, file_path):
        """

    

        https://api.mendeley.com/apidocs#!/document-from-file/createDocumentFromFileUpload
        
        TODO: We might want some control over the naming
        TODO: Support retrieval from another website
        
        """
        filename = basename(file_path)
        headers = {
            'content-disposition': 'attachment; filename=%s' % filename,
            'content-type': mimetypes.guess_type(filename)[0]}

        # TODO: This needs futher work
        pass

    def delete(self):
        """
        https://api.mendeley.com/apidocs#!/documents/deleteDocument
        """
        pass

    def update(self, doc_id, new_data):
        """
        https://api.mendeley.com/apidocs#!/documents/updateDocument
        """
        url = BASE_URL + '/documents/' + doc_id

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        return self.parent.make_patch_request(url, models.Document, new_data, headers=headers)

    def move_to_trash(self, doc_id):

        url = BASE_URL + '/documents/' + doc_id + '/trash'

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        resp =  self.parent.s.post(url, headers=headers, auth = self.parent.access_token)
        return

class Files(object):
    
    def __init__(self, parent):
        self.parent = parent

    def get_single(self, **kwargs):
        """
        # https://api.mendeley.com/apidocs#!/annotations/getFiles

        THIS DOESN'T REALLY DO ANYTHING RIGHT NOW.

        Parameters
        ----------
        id :
        document_id :
        catalog_id :
        filehash :
        mime_type :
        file_name :
        size :

        Returns
        -------

        """

        url = BASE_URL + '/files'

        doc_id = kwargs.get('document_id')

        # Not sure what this should be doing
        response_params = {'document_id': doc_id}

        # Didn't want to deal with make_get_request
        response = self.parent.s.get(url, params=kwargs, auth=self.parent.access_token)
        json = response.json()[0]

        file_id = json['id']

        file_url = url + '?id=' + file_id

        file_response = self.parent.s.get(file_url, auth=self.parent.access_token)

        return file_id

        pass

    def link_file(self, file, params, file_url=None):
        """

        Parameters
        ----------
        file : dict
            Of form {'file' : Buffered Reader for file}
            The buffered reader was made by opening the pdf using open().
        params : dict
            Includes the following:
            'title' = paper title
            'id' = ID of the document to which
            the file will be attached
            (optional) '_return_type': return type of API.make_post_request
            (json, object, raw, or response)

        Returns
        -------
        Object specified by params['_return_type'].
            Generally models.LinkedFile object

        """
        url = BASE_URL + '/files'

        # Extract info from params
        title = params['title']
        doc_id = params['id']
        object_fh = models.File

        # Get rid of spaces in filename
        filename = urllib_quote(title) + '.pdf'
        filename = filename.replace('/', '%2F')

        headers = dict()
        headers['Content-Type'] = 'application/pdf'
        headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        headers['Link'] = '<' + BASE_URL + '/documents/' + doc_id + '>; rel="document"'

        API.make_post_request(API(), url, object_fh, params, headers=headers, files=file)

    def link_file_from_url(self, file, params, file_url):
        """

        Parameters
        ----------
        file : dict
            Of form {'file' : Buffered Reader for file}
            The buffered reader was made by opening the pdf using open().
        params : dict
            Includes paper title, ID of the document to which
            the file will be attached, and return type.
        file_url : str
            Direct URL to a pdf file.

        Returns
        -------
        Object specified by params['_return_type'].
            Generally models.LinkedFile object

        """
        url = BASE_URL + '/files'

        # Extract info from params
        title = params['title']
        doc_id = params['id']
        object_fh = models.LinkedFile

        # Get rid of spaces in filename
        filename = title.replace(' ', '_') + '.pdf'

        headers = dict()
        headers['Content-Type'] = 'application/pdf'
        headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        headers['Link'] = '<' + BASE_URL + '/documents/' + doc_id + '>; rel="document"'

        API.make_post_request(API(), url, object_fh, params, headers=headers, files=file)

    def delete(self):
        # TODO: make this work
        pass

class Folders(object):
    def __init__(self, parent):
        self.parent = parent

    def create(self, name):
        url = BASE_URL + '/folders'

        # Clean up name
        name = name.replace(' ', '_')
        name = urllib_quote(name)
        params = {'name' : name}

        headers = {'Content-Type' : 'application/vnd.mendeley-folder.1+json'}

        return self.parent.make_post_request(url, models.Folder, params, headers=headers)


class MetaData(object):
    # https://api.mendeley.com/apidocs#!/metadata/getDocumentIdByMetadata
    pass


class Profiles(object):
    
    def __init__(self,parent):
        self.parent = parent
        
        #TODO: If public, provide no "me" method
        
    def get(self, **kwargs):
        """
        https://api.mendeley.com/apidocs/docs#!/profiles/getProfiles
        https://api.mendeley.com/apidocs/docs#!/profiles/get
        
        """
        pass
    
    def me(self):
        """
        https://api.mendeley.com/apidocs/docs#!/profiles/getProfileForLoggedInUser
        """
        pass
    
    #def update_my_profile()   => Let's implement this in the profile model
    


class Trash(object):
    def __init__(self, parent):
        self.parent = parent

    def get(self, **kwargs):
        """       
        
        Online Documentation
        --------------------
        https://api.mendeley.com/apidocs/docs#!/trash/getDeletedDocuments        
        https://api.mendeley.com/apidocs/docs#!/trash/getDocument        
        
        Parameters
        ----------
        id : 
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order            
        view : 
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'
        """

        url = BASE_URL + '/trash'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        view = kwargs.get('view')

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit, 'page_id':0}

        verbose = _process_verbose(self.parent,kwargs,response_params)

        if verbose:
            print("Requesting up to %d trash documents from Mendeley with params: %s" % (limit, kwargs))            
            
        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

    def delete(self, **kwargs):
        pass
    
    def restore(self, **kwargs):
        pass


def convert_datetime_to_string(d, key):
    if key in d and isinstance(d[key], datetime):
        d[key] = d[key].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
def _process_verbose(api,kwargs,response_params):
    
    """
    
    Parameters
    ----------
    api : API
        Contains .verbose attribute
    kwargs : dict
        Options from the user
    response_params : dict or None
        Values for the response model. 
        
    
    1) Allow user to make each call verbose or not.
    2) Have default from main API that gets called if user input is not present.
    3) Update response_params to include verbose value (for models) 
    
    """
    
    if 'verbose' in kwargs:
        verbose = kwargs.pop('verbose')
    else:
        verbose = api.verbose   
    
    if response_params is not None:
        response_params['verbose'] = verbose
    
    return verbose
