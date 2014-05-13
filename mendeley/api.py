# -*- coding: utf-8 -*-
"""

This module is meant to implement all functions described at:




"""

from . import auth
import requests
import pdb
from . import api_user_results as uresults

class UserMethods():

    """
    This class exposes API calls that are specific to a user.
        
    
    """
    
    BASE_URL = 'https://api-oauth2.mendeley.com/oapi/'    
    
    def __init__(self, username = None):
        self.access_token = auth.UserAccessToken.load(username)
        
        #Other potential properties:
        #- return raw
        #- 
           
    def make_get_request(self, url, params = None, good_status = 200):
                
        """

        Parameters:
        ----------------------------------------            
        url : str
            URL to go to
        params : dict (default {})
            Dictionary of paraemters to place in the GET query. Values may be
            numbers or strings.
        good_status : int (default 200)
            The status to check for as to whether or not the request 
            was successful.
        """
        
        if params is None:
            params = {}
        else:
            params = dict((k, v) for k, v in params.iteritems() if v) 
        
        #TODO: I will probably add on variable returns types - raw json or 
        # the parsed object 
        #        
        
            
        
        r = requests.get(url,params=params,auth=self.access_token)
        
        if r.status_code != good_status:
            raise Exception('Call failed') #TODO: This should be improved
                    
        return r


    """
    ===========================================================================
                                Stats Methods
    ===========================================================================
    """
    def stats_authors():
        """
        Returns list of top 5 authors in user library.
        
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-authors-stats 
        """
        pass
        
    
    def stats_tags():
        pass
    
    def stats_publications():
        pass

    """
    ===========================================================================
                                Documents Methods
    ===========================================================================
    """


    def docs_get_library_ids(self, page=0, items=20):
        """
        Returns a set of IDs that the user has in their library. These ID's 
        uniquely identify library entries.          
         
        Parameters:
        -----------
        page  : int, str (default 0)
            Page # to get, 0 based.
        items : int, str (default 20)
            Maximum # of items per page to return.
     
        
        
        Returns:
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library
        """
    
        url = self.BASE_URL + 'library/'
    
        params = {
            'page' :  page,
            'items':  items}

        r = self.make_get_request(url,params)    
    
        return uresults.LibraryResponse(r.json())
   
    def docs_get_user_authored():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-authored
        """
        pass
    
    def docs_get_details():
        """
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library-document-details
        """
        pass
    
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
    
    def profile_get_info(self, profile_id = 'me', section=None, subsection=None):
        """
        Returns information about a user.
        
        Parameters:
        -----------
        profile_id : int or str (default 'me')
            The string 'me' can be used to request information about the
            user whose access token we are using. A numeric value can be used
            to get someone else's contact info.
        section : {'main','awards','cv','contact'} (optional)
        
                
        
        """
        
        url = self.BASE_URL + 'profiles/info/%s/' % (profile_id)
    
        params = {
            'section'   :  section,
            'subsection':  subsection}

        r = self.make_get_request(url,params)    
    
        return uresults.ProfileInfo(r.json())
        