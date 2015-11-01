# -*- coding: utf-8 -*-
"""

This module is meant to implement all functions described at:

http://apidocs.mendeley.com/home/public-resources
&
http://apidocs.mendeley.com/home/user-specific-methods


"""

import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    from urllib2 import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

from . import auth
import requests
import pdb
from . import api_user_results as uresults
from . import api_public_results as presults

class _APIMethods(object):
    
    """
    This is a shared superclass for both the public and private API classes.
    """
    
    BASE_URL = 'https://api.mendeley.com' 

    #TODO: Have something that indicates that access_token is required
    #for subclasses to have ...

    @staticmethod
    def fix_url_input(input_data):
        
        """
            This is basically a call to encode an input for GET requests so
            that they are valid parameters or values for the URL
            
            Parameters
            ----------
            input_data
        """        
        
        return urllib_quote(input_data,'')
        #TODO: Not sure what this code was doing, need to test Python 2 again
#        if isinstance(input_data, basestring):
#            return urllib_quote(input_data,'')
#        else:
#            return urllib_quote(str(input_data),'')
        

    def make_get_request(self, url, object_fh, params = None, good_status = 200, return_type = 'object'):
                
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
        return_type : {'object','json','raw'}
            object - indicates that the result class object should be created.
                This is the slowest option but provides the most functionality.
            json   - 
            
        See Also:
        ---------
        .auth.UserCredentials.__call__()
        .auth.PublicCredentials.__call__()
        """
        
        if params is None:
            params = {}
        else:
            if PY2:
                params = dict((k, v) for k, v in params.iteritems() if v)
            else:
                params = dict((k, v) for k, v in params.items() if v)
        
        #TODO: Create a session object and work off of that
                    
        #NOTE: We make authorization go through the access token. The request
        #will call the access_token prior to sending the request. Specifically
        #the __call__ method is called.
        r = requests.get(url,params=params,auth=self.access_token)      
        
        if r.status_code != good_status:
            print(r.text)
            print('')
            #TODO: This should be improved
            raise Exception('Call failed with status: %d' % (r.status_code)) 
        
        
        if return_type is 'object':
            return object_fh(r.json(),self)
        elif return_type is 'json':
            return r.json()
        elif return_type is 'raw':
            return r.text
        else:
            raise Exception('No match found for return type')
            
        return r


class PublicMethods(_APIMethods):
    
    """
    This class exposes the public methods of the API.
    
    Example:
    --------
    from mendeley import api
    pm = api.PublicMethods()
    ta = pm.get_top_authors()
    """
    
    def __init__(self):
        self.access_token = auth._get_public_credentials()
        pass
    
    """
    ===========================================================================
                                Stats Methods
    ===========================================================================
    """
    
    def get_top_authors(self,discipline_id = None):
        """
        Returns list of all-time top authors across all disciplines, 
        unless a discipline is specified.
        
        Parameters:
        -----------
        discipline_id : int, str (default None)
            Discipline ID is an enumeration of disciplines. This list comes
            from the method get_disciplines
            
        Returns:
        --------
        list of mendeley.api_user_results.TopAuthor
        """        
        
        url = self.BASE_URL + 'stats/authors/'
    
        params = {
            'discipline'   :  discipline_id}

        r = self.make_get_request(url,params)    

        #NOTE: We might not get JSON ... 
        temp_json = r.json()
        return [presults.TopAuthor(x) for x in temp_json]
        
    """
    ===========================================================================
                                Search Methods
    ===========================================================================
    """        
    
    def search_Mendeley_catalog(self,terms,page=0,items=20):
        """
        Searches Mendeley catalog for entries with matches.
        
        @DOC: http://apidocs.mendeley.com/home/public-resources/search-terms
        """
        
        url = self.BASE_URL + 'documents/search/%s/' % (self.fix_url_input(terms))        
       
        params = {
            'page'   :  page,
            'items'  :  items}       
       
        r = self.make_get_request(url,params)
        pdb.set_trace()       
       
        #TODO: Build response
        #total_results
        #items_per_page
        #total_pages
        #current_page
        #documents       
       
        return None
    
    def get_entry_details(self,id,id_type='Mendeley'):
        """
        
        Parameters:
        -----------
        id : int, str
        id_type : {'Mendeley','arxiv','doi','isbn','pmid','scopus','ssm'}
            
        @DOC: http://apidocs.mendeley.com/home/public-resources/search-details
        """
        
        url = self.BASE_URL + 'documents/details/%s/' % (self.fix_url_input(id))     
        
        if id_type is 'Mendeley':
            id_type = None #No type means use Mendeley canonical ID
        
        params = {
            'type'   :  id_type}       
       
        r = self.make_get_request(url,params)
       
        return uresults.PublicJournalArticle(r.json())
    
    def get_related_papers(self,id):
        """
        Returns list of up to 20 research papers related to the queried 
        canonical id.
        
        @DOC: http://apidocs.mendeley.com/home/public-resources/search-related
        """
        url = self.BASE_URL + 'documents/related/%s/' + id
        
        r = self.make_get_request(url)
        pdb.set_trace()
        
        return None
        
    def get_pubs_with_name(self,name,page=0,items=20,year=None):
        """
        Returns list of publications with that author name.
        
        @DOC: http://apidocs.mendeley.com/home/public-resources/search-authored        
        """
        
        url = self.BASE_URL + 'documents/authored/%s/' + self.fix_url_input(name)

        params = {
            'page'   :  page,
            'items'  :  items,
            'year'   :  year}

        r = self.make_get_request(url,params)
        pdb.set_trace()
        
        return None

class UserMethods(_APIMethods):

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
        
    
        
        
    def __init__(self, user_name = None):
        """
        
        Parameters:
        -----------
        user_name : str (default None)
            If no input is specified the default user will be used.        
        """

        #TODO: Could allow changing default return type for the methods
        #i.e. from an object to the raw json

        self.access_token = auth.UserCredentials.load(user_name)
    

    #New Code
    #=====================================================================
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

        return self.make_get_request(url,uresults.ProfileInfo,params)    
    
    def docs_get_details(self):
        """

        Parameters
        ----------
        view
            - 'bib'
            - 'client'
            - 'tags'
            - 'patent'
            - 'all'
        profile_id
        group_id
        modified_since
        deleted_since
        limit : string or int (default 20)
            Largest allowable value is 500
        order
        sort

        
        """
        url = self.BASE_URL + '/documents/'
            
        params = {}

        return self.make_get_request(url,uresults.get_document_set,params)   



    #Old Code
    #=====================================================================

               
    @property
    def user_name(self):
        return self.access_token.user_name

    """
    ===========================================================================
                                Stats Methods
    ===========================================================================
    """
    def stats_authors(self):
        """
        Returns list of top 5 authors in user library.
        
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-authors-stats 
        """

        url = self.BASE_URL + 'library/authors/'
    
        params = {}

        r = self.make_get_request(url,params)    
    
        return uresults.LibraryIDs(r.json(),self)
        
    
    def stats_tags():
        pass
    
    def stats_publications():
        pass

    """
    ===========================================================================
                                Documents Methods
    ===========================================================================
    """


    def docs_get_library_ids(self, page=0, items=20, get_all=False, **kwargs):
        """
        Returns a set of IDs that the user has in their library. These ID's 
        uniquely identify library entries.          
         
        Parameters:
        -----------
        page  : int, str (default 0)
            Page # to get, 0 based.
        items : int, str (default 20)
            Maximum # of items per page to return.
        get_all : logical (default False)
            If true this returns all ids in the library.
            
        See Also:
        ---------
        .api._APIMethods.make_get_request
        .api_user_results.LibraryIDsContainer

        Returns:
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library
        """

        if get_all is True:
            temp = self.docs_get_library_ids(page=0,items=1)
            return self.docs_get_library_ids(page=0,items=temp.n_entries_in_lib)
    
        url = self.BASE_URL + 'library/'
    
        params = {
            'page' :  page,
            'items':  items}

        object_fh = uresults.LibraryIDs;
        return self.make_get_request(url,object_fh,params)    
       
    def docs_get_user_authored():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-authored
        """
        pass
    
#    def docs_get_details(self, id, **kwargs):
#        """
#        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library-document-details
#        """
#        
#        url = self.BASE_URL + 'library/documents/%s/' % (id)    
#        
#        params = {}
#        
#        import pdb
#        pdb.set_trace()
#        
#        r = self.make_get_request(url,params)  
#        
#        return r.json()
#        
#        pass
    
    def docs_create_new():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library-create-document
        """
        
    def docs_update():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library-update-document
        """
   
    def docs_upload_file():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/file-upload
        """
    def docs_download_file():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/download-file
        """
        
    def docs_delete():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library-remove-document
        """
        
    """
    ===========================================================================
                                Profile  Method
    ===========================================================================
    """
    

     
    def __repr__(self):
        #TODO: Add on current user ...
        return \
        'Stats Methods:\n' + \
        '   stats_authors\n' + \
        '   stats_tags\n' + \
        '   stats_publications\n' + \
        'Document Methods:\n' + \
        '   docs_get_library_ids - DONE\n' + \
        '   docs_get_user_authored\n' + \
        '   docs_get_details\n' + \
        '   docs_create_new\n' + \
        '   docs_update\n' + \
        '   docs_upload_file\n' + \
        '   docs_download_file\n' + \
        '   docs_delete\n' + \
        'Profile Methods:\n' + \
        '   profile_get_info\n'
        
        
        