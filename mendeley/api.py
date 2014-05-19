# -*- coding: utf-8 -*-
"""

This module is meant to implement all functions described at:




"""

import urllib2
from . import auth
import requests
import pdb
from . import api_user_results as uresults

class _APIMethods(object):
    
    BASE_URL = 'https://api-oauth2.mendeley.com/oapi/' 

    #TODO: Have something that indicates that access_token is required
    #for subclasses to have ...

    @staticmethod
    def fix_url_input(input_data):
        
        if isinstance(input_data, basestring):
            return urllib2.quote(input_data,'')
        else:
            return urllib2.quote(str(input_data),'')
        

    def make_get_request(self, url, params = None, good_status = 200):
                
        """

        Parameters:
        -----------          
        url : str
            URL to go to
        params : dict (default {})
            Dictionary of paraemters to place in the GET query. Values may be
            numbers or strings.
        good_status : int (default 200)
            The status to check for as to whether or not the request 
            was successful.
            
        See Also:
        ---------
        .auth.UserAccessToken.__call__()
        .auth.PublicAccessToken.__call__()
        """
        
        if params is None:
            params = {}
        else:
            params = dict((k, v) for k, v in params.iteritems() if v) 
        
        #TODO: I will probably add on variable returns types - raw json or 
        # the parsed object 
        #        
        
            
        #NOTE: We make authorization go through the access token. The request
        #will call the access_token prior to sending the request. Specifically
        #the __call__ method is called.
        r = requests.get(url,params=params,auth=self.access_token)      
        
        if r.status_code != good_status:
            print(r.text)
            print('')
            raise Exception('Call failed with status: %d' % (r.status_code)) #TODO: This should be improved
                    
        return r


class PublicMethods(_APIMethods):
    
       
    
    def __init__(self):
        self.access_token = auth.get_public_credentials()
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
        """        
        
        url = self.BASE_URL + 'stats/authors/'
    
        params = {
            'discipline'   :  discipline_id}

        r = self.make_get_request(url,params)    

        #NOTE: We might not get JSON ... 
        temp_json = r.json()
        return [uresults.TopAuthor(x) for x in temp_json]
        
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
        
    
    """
    
    BASE_URL = 'https://api-oauth2.mendeley.com/oapi/'    
    
    def __init__(self, username = None):
        self.access_token = auth.UserAccessToken.load(username)
        
        #Other potential properties:
        #- return raw
        #- 
           



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
        