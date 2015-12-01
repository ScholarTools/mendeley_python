# -*- coding: utf-8 -*-
"""

This module is meant to implement all functions described at:
http://dev.mendeley.com/methods/

General Usage
-------------
from mendeley import api as mapi
um = mapi.UserMethods()
pm = mapi.PublicMethods()

Request Options
---------------
In addition to the options of a given function, the following options are also
supported:
TODO: fill this in: example _return_type

TODO: Create an options class that can be given to the request (e.g. for return type)


Improvements
------------
1) Move functions with static info into a subclass
- academic_statuses
- disciplines


Methods
-------
academic_statuses

"""

import sys
import mimetypes
from os.path import basename

PY2 = int(sys.version[0]) == 2

if PY2:
    from urllib2 import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

from . import auth
import requests
import pdb
from . import models


BASE_URL = 'https://api.mendeley.com' 
catalog_fcns = {None:models.CatalogDocument,
                'bib':models.BibCatalogDocument,
               'stats':models.StatsCatalogDocument,
               'client':models.ClientCatalogDocument,
               'all':models.AllCatalogDocument
               }

document_fcns = {None:models.Document,
                'bib':models.BibDocument,
                'client':models.ClientDocument,
               'tags':models.TagsDocument,
               'stats':models.StatsDocument,
               'all':models.AllDocument
               }

class API(object):
    
    """
    This is a shared superclass for both the public and private API classes.
    
    Attributes
    ----------
    default_return_type : {'object','json','raw','response'}
        This is the default type to return from methods.
        
    last_response : 
    last_params : 
        
    """
    
    

    def __init__(self,user_name=None):
        """
        Parameters
        ----------
        user_name :
        """
        #TODO: Decide how I want to handle this
        #In the old approach None means use the default user ...
        self.public_only = False        
        #self.public_only = user_name is None
        
        #if user_name is None:
        #    token = auth._get_public_credentials()
        #else:
        token = auth.UserCredentials.load(user_name)
       
       #TODO: Add on printing of object with methods and default options
        
        self.default_return_type = 'object'
        self.access_token = token
        self.s = requests.Session()
        self.last_response = None
        self.last_params = None
        
        self.annotations = Annotations(self)
        self.definitions = Definitions(self)
        self.documents = Documents(self)

    @property
    def user_name(self):
        if self.public_only:
            return None
        else:
            return self.access_token.user_name

    def make_post_request(self, url, object_fh, params, response_params=None, headers=None):
        
        #I'd like to be able to merge this with the get request method
        #
        #This code is currently in flux ...        
        
        #http://docs.python-requests.org/en/latest/user/advanced/#streaming-uploads
        #files=files
    
        return_type = params.pop('_return_type',self.default_return_type)   
    
        r = self.s.get(url,params=params,auth=self.access_token, headers=None)   

    def make_get_request(self, url, object_fh, params, response_params=None):
                
        """

        Parameters:
        -----------          
        url : str
            URL to make request from.
        object_fh: function handle
            
        params : dict (default {})
            Dictionary of paraemters to place in the GET query. Values may be
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
        
        #TODO: extract good_status = 200, return_type = None from params        

        if params is None:
            params = {}
        else:
            if PY2:
                params = dict((k, v) for k, v in params.iteritems() if v)
            else:
                params = dict((k, v) for k, v in params.items() if v)
        
        return_type = params.pop('_return_type',self.default_return_type)
                            
        #NOTE: We make authorization go through the access token. The request
        #will call the access_token prior to sending the request. Specifically
        #the __call__ method is called.
        r = self.s.get(url,params=params,auth=self.access_token)      
        
        self.last_url = url
        self.last_response = r     
        self.last_params = params
                
        if not r.ok:
        #if r.status_code != good_status:
            print(r.text)
            print('')
            #TODO: This should be improved
            raise Exception('Call failed with status: %d' % (r.status_code)) 
        
        
        if return_type is 'object':
            if response_params is None:
                return object_fh(r.json(),self)
            else:
                return object_fh(r.json(),self,response_params)
        elif return_type is 'json':
            return r.json()
        elif return_type is 'raw':
            return r.text
        elif return_type is 'response':
            return r
        else:
            raise Exception('No match found for return type')
            

        
    def catalog(self,**kwargs):
        
        """
        
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
        response_params = {'fcn':catalog_fcns[view]}

        return self.make_get_request(url,models.DocumentSet.create,kwargs,response_params)


      
        
class Definitions(object):

    """
    TODO: These values should presumably only be queried once ...
    """
    def __init__(self,parent):
        self.parent = parent 
        
    def academic_statuses(self,**kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/academic_statuses/get
        
        Example
        -------        
        from mendeley import API
        m = API()
        a_status = m.definitions.academic_statuses()
        """
        url = BASE_URL + '/academic_statuses'
                
        return self.parent.make_get_request(url,models.academic_statuses,kwargs)
        
    def disciplines(self,**kwargs):
        """
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.disciplines()
        """
        url = BASE_URL + '/disciplines'
                
        return self.make_get_request(url,models.disciplines,kwargs)

        
    def document_types(self,**kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/document_types/getAllDocumentTypes
        
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.document_types()
        """
        url = BASE_URL + '/document_types'
                
        return self.parent.make_get_request(url,models.document_types,kwargs)  
    
class Annotations(object):
    
    def __init__(self,parent):
        self.parent = parent
        
    def get():
        #https://api.mendeley.com/apidocs#!/annotations/getAnnotations
        pass
    
    def delete():
        pass
    
class Documents(object):
    
    def __init__(self,parent):
        self.parent = parent
        
    def get(self,**kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/getDocuments
        
        Parameters
        ----------
        id : 
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        deleted_since : string
            Returns only documents deleted since this timestamp. Should be 
            supplied in ISO 8601 format.
        profile_id : string
            The id of the profile that the document belongs to, that does not 
            belong to any group. If not supplied returns users documents.
        authored :
            TODO
        starred : 
        limit : string or int (default 20)
            Largest allowable value is 500
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order            
        view
            - 'bib'
            - 'client'
            - 'tags'
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

        view = kwargs.get('view')
        response_params = {'fcn':document_fcns[view]}  
                
        return self.parent.make_get_request(url,models.DocumentSet.create,kwargs,response_params)  
        
    def create(self,kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/createDocument
        """
        pass
    
    def create_from_file(self,file_path):
        """
        TODO: We might want some control over the naming
        TODO: Support retrieval from another website

        https://api.mendeley.com/apidocs#!/document-from-file/createDocumentFromFileUpload
        
        """
        filename = basename(file_path)
        headers = {
            'content-disposition': 'attachment; filename=%s' % filename,
            'content-type': mimetypes.guess_type(filename)[0]}
            
        #TODO: This needs futher work
        pass
    
    def delete(self):
        """
        https://api.mendeley.com/apidocs#!/documents/deleteDocument
        """
        pass
    
    def update(self):
        """
        https://api.mendeley.com/apidocs#!/documents/updateDocument
        """
        pass
    
    def move_to_trash(self):
        pass
    
    
    
class MetaData(object):
#https://api.mendeley.com/apidocs#!/metadata/getDocumentIdByMetadata    
    pass

    
class UserMethods(API):

    """
    This class exposes API calls that are specific to a user.
        
    Example:
    --------
    #TODO: Explain how to get user credentials
    
    #The example below assumes the user credentials have already been acquired
    #and thata default user is specified in the configuration file.
    
    from mendeley import api
    um = api.UserMethods()
    lib_ids = um.docs_get_library_ids(items=100)
    
    """
            



    def profile_get_info(self, profile_id = 'me'):
        """
        
        TODO: This may no longer be specific to the user. We should
        write 2 methods, 1 for public and 1 for user
        
        Returns information about a user.
        
        http://dev.mendeley.com/methods/#profiles
        
        Parameters
        ----------
        profile_id : string (default 'me')
            The string 'me' can be used to request information about the
            user whose access token we are using. A numeric value can be used
            to get someone else's contact info.        
        """
        
        url = self.BASE_URL + '/profiles/' + (profile_id)
            
        params = {}

        return self.make_get_request(url,models.ProfileInfo,params)    
    
    def docs_get_details(self,**kwargs):
        """
        
        Parameters
        ----------
        view
            - 'bib'
            - 'client'
            - 'tags'
            - 'patent'
            - 'all'
        profile_id : string
            The id of the profile that the document belongs to, that does not 
            belong to any group. If not supplied returns users documents.
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        deleted_since : string
            Returns only documents deleted since this timestamp. Should be 
            supplied in ISO 8601 format.
        limit : string or int (default 20)
            Largest allowable value is 500
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'
            
        Examples
        --------
        from mendeley import api as mapi
        um  = mapi.UserMethods()
        
        1) No options
        docs = um.docs_get_details()


        
        """
        #TODO: Add on more usage examples
        url = self.BASE_URL + '/documents/'
            
        params = kwargs

        return self.make_get_request(url,models.DocumentSet,params)

    def __repr__(self):

        return \
        'Current User: %s\n' % self.user_name +\
        'Methods:\n' + \
        '   profile_get_info\n' +\
        '   docs_get_details\n'
        
        
        