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
from . import models

class _APIMethods(object):
    
    """
    This is a shared superclass for both the public and private API classes.
    
    Attributes
    ----------
    default_return_type : {'object','json','raw','response'}
        This is the default type to return if 
        
    """
    
    BASE_URL = 'https://api.mendeley.com' 

    #TODO: Have something that indicates that access_token is required
    #for subclasses to have ...
    def __init__(self,token):
        self.default_return_type = 'object'
        self.access_token = token
        self.s = requests.Session()
        self.last_response = None
        self.last_params = None

    def make_get_request(self, url, object_fh, params = None):
                
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
        
        #TODO: Create a session object and work off of that
                    
        #NOTE: We make authorization go through the access token. The request
        #will call the access_token prior to sending the request. Specifically
        #the __call__ method is called.
        r = self.s.get(url,params=params,auth=self.access_token)      
        
        self.last_response = r     
        self.last_params = params
                
        if not r.ok:
        #if r.status_code != good_status:
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
        elif return_type is 'response':
            return r
        else:
            raise Exception('No match found for return type')



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
        super(PublicMethods, self).__init__(token=auth._get_public_credentials())
        
    def academic_statuses(self,**kwargs):
        """
        Example
        -------        
        from mendeley import api as mapi
        pm  = mapi.PublicMethods()
        
        a_status = pm.academic_statuses()
        """
        url = self.BASE_URL + '/academic_statuses'
        
        params = kwargs
        
        return self.make_get_request(url,models.academic_statuses,params)
        
#    def identifier_types(self,**kwargs):
#
#        params = kwargs
#
#        return self.make_get_request(url,models.DocumentSet,params)
        
    
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
        super(UserMethods, self).__init__(token=auth.UserCredentials.load(user_name))

    
    @property
    def user_name(self):
        return self.access_token.user_name


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
        
        
        