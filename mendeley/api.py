# -*- coding: utf-8 -*-
"""

"""

from . import auth
import requests
import pdb
from . import api_user_results as uresults

class UserMethods():

    """

        
    
    """
    
    BASE_URL = 'https://api-oauth2.mendeley.com/oapi/'    
    
    def __init__(self,username = None):
        self.access_token = auth.AccessToken.load(username)
           
    def makeGetRequest(self,url,params = {},good_status = 200):
                
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
        
        r = requests.get(url,params=params,auth=self.access_token)
        
        if r.status_code != good_status:
            raise Exception('Call failed') #TODO: This should be improved
                    
        return r

    def get_library_ids(self, page=0, items=20):
    
        """
         
        Returns a set of IDs that the user has in their library.          
         
        Parameters:
        -----------------------------------
        page  : int, str (default 0)
            Page # to get, 0 based.
        items : int, str (default 20)
            Maximum # of items per page to return.
     
        @DOC: http://apidocs.mendeley.com/home/user-specific-methods/user-library
        """
    
        url = self.BASE_URL + 'library/'
    
        params = {
            'page' :    page,
            'items':    items}

        #pdb.set_trace()           
           
        r = self.makeGetRequest(url,params)    
    
        return uresults.LibraryResponse(r.json())
    
    