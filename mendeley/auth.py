# -*- coding: utf-8 -*-
"""
This module is meant to handle things related to authentication for the
Mendeley API.

In general it is better to interact with the API directly, rather than
interacting with this module.

Mendeley Authethentication Documentation:
http://apidocs.mendeley.com/home/authentication

Important Methods
-----------------




"""
import requests
from requests.auth import AuthBase

import datetime
import pytz #This seems to be a 3rd party library but is installed on
#my local Python installation (Py Timze Zones)

import pickle
import os

from . import utils
from . import config

"""
-------------------------------------------------------------------------------
These are methods that other modules might want to access directly.

"""

def retrieve_public_credentials():

    """
    Loads public credentials

    Returns:
    --------
    PublicCredentials    
    """
    
    if PublicCredentials.token_exists_on_disk():
        return PublicCredentials.load()
    else:
        r = PublicCredentials._make_request_for_token()
        
        pat = PublicCredentials(r)
    
        pat.save()    
    
        return pat
        
def retrieve_user_credentials():
    pass
        
"""
-------------------------------------------------------------------------------
"""
#%% 


class _Credentials(AuthBase):
    
    """
    This is a superclass for:
    UserCredentials
    PublicCredentials
    
    TODO: I currently have a lot of duplicated code between the two classes that
    needs to be moved to here.
    # - get_file_path()
    # - renew_token_if_necessary()
    
    Attributes
    ----------
    token_expired : 
    expires : timestamp
    """
 
    """
    Abstract Methods
    ----------------
    renew_token
    
    """
    #The amount of time prior to token expiration that a request should be
    #made to renew the token. See self.renew_token_if_necessary()
    #I'm trying to avoid the following:
    # 1) check for valid token
    # 2) token becomes invalid
    # 3) request with invalid token
    #
    #Default value: check if there is less than 1 minute
    RENEW_TIME = datetime.timedelta(minutes = 1) 
    
    AUTH_URL = 'https://api-oauth2.mendeley.com/oauth/token'   
   
    @staticmethod
    def get_save_base_path(create_folder_if_no_exist = False):
        """
        The API credentials are stored at:
        <repo_base_path>/data/credentials
        
        NOTE: Anything in the data folder is omitted from versioning using
        .gitignore
        """
        
        return utils.get_save_root(['credentials'],create_folder_if_no_exist)

    @property
    def token_expired(self):        
        """
        Determine if the token has expired. As of this writing
        the token expires 1 hour after being granted.
        """

        time_diff = self.expires - datetime.datetime.now(pytz.utc)
      
        return time_diff.total_seconds() < 0 
        
    def renew_token_if_necessary(self):
      
        """
        Renews the access token if it has expired or is about to expire.
        """
      
        if datetime.datetime.now(pytz.utc) + self.RENEW_TIME > self.expires:
            self.renew_token()
            
    def __call__(self,r):
        
        """
        This method is called before a request is sent.
        
        Parameters
        ----------
        r : Requests Object
        
        See Also
        --------
        .api.PublicMethods
        """
        #Called before request is sent
          
        self.renew_token_if_necessary()
        
        r.headers['Authorization'] =  "bearer " + self.access_token
        
        return r 
        
    @classmethod
    def does_token_exist(cls,user_name):
        """
        For public use 'public'
        """
        load_path = cls.get_file_path(user_name)
        return os.path.isfile(load_path)
        
    @classmethod
    def get_file_path(cls,user_name,create_folder_if_no_exist = False):
        """     
        Provides a consistent path to where this object can be saved and loaded
        from.
        
        Parameters:
        -----------
        user_name: str
            See class initialization for definition.
        
        Returns:
        -------
        str
        
        """

        save_name = utils.user_name_to_file_name(user_name) + '.pickle'

        save_folder_path = cls.get_save_base_path(create_folder_if_no_exist)
        
        final_save_path  = os.path.join(save_folder_path,save_name)
        
        return final_save_path
        
    def populate_session(self,session=None):
        if session is None:
            self.session = requests.Session() 
        else:
            self.session = session
        
    def save(self):
        
        """
        Saves the class instance to disk.
        """
        save_path = self.get_file_path(create_folder_if_no_exist = True)
        with open(save_path, "wb") as f:
            pickle.dump(self,f)

class UserCredentials(_Credentials):
    
    """
    This class represents an access token (and refresh token). An access token 
    allows a program to access user specific information. This class should 
    normally be retrieved by:
    
    #TODO: replace with functions
    1) Calling UserCredentials.load(user_name)
    2) Calling get_access_token(user_name,password)
    
    Attributes
    ----------
    version : string
        The current version of the access token. Since these are saved to disk
        this value is retained in case we need to make changes.
    user_name : string
    access_token : string
        The actual access token. This might be renamed ...
    token_type : str
        I'm not really sure what this is for. It is currently sent in response
        to a request for an access token but I'm not using it. Currently the 
        value is "bearer"
        
    JAH NOTE: I'm not thrilled with the name of this class ...
    #UserAccess instead? - just this implies it only handles the access token
    """  
    
    
       
    
    def __init__(self, user_name=None, user_info=None):
        """
        Parameters
        ----------
        json : dict
        user_info : UserInfo
            
        """
        if user_name is not None:
            user_info = ConfigUserInfo(user_name)
            import pdb
            pdb.set_trace()
        
        self.version = 1
        self.user_name = user_info.user_name
        self.
        self.init_json_attributes(json)
     
    @staticmethod   
    def create_initial_token():
        pass
        
    def init_json_attributes(self, json):
        """
        Mendeley will return json from the http request.
        
        Ignoring token_type attribute (generally/always? with 'bearer' value)
        """
        self.access_token  = json['access_token']
        self.token_type    = json['token_type']
        self.refresh_token = json['refresh_token']
        #We'll work with utc just in case someone moves between time zones
        self.expires       = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=json['expires_in'])
        
        return None

    def __repr__(self):
        pv = ['version',self.version,'user_name',self.user_name,
              'access_token',self.access_token,'token_type',self.token_type,
              'refresh_token',self.refresh_token,'expires',self.expires,
              'token_expired',self.token_expired]
      
    def renew_token(self):     
        """
        Renews the access token so that requests can be made for user data.      
      
        NOTE: The refresh_token can be used even after the access token has 
        expired.
        """      
        
        client_auth = requests.auth.HTTPBasicAuth(
            config.Oauth2Credentials.client_id,
            config.Oauth2Credentials.client_secret)
        
        post_data = {"grant_type"   :   "refresh_token",
                     "refresh_token":   self.refresh_token}
       
        #TODO: We should replace this with the session object            
        r = requests.post(self.AUTH_URL,auth=client_auth,data=post_data)
      
        #Observed errors:
        #----------------------------------
        #1) {"error":"invalid_grant","error_description":"Invalid grant"}
        #
        # - Seems to have been fixed by deleting the pickled version of this
        #   class that was associated with the user in /data/credentials
              
        if r.status_code != requests.codes.ok:
            print(r.text)
            import pdb
            pdb.set_trace()
            raise Exception('TODO: Fix me, request failed ...')
      
        self.init_json_attribute(r.json())      
        self.save()

    

        
    @classmethod
    def load(cls, user_name = None, create_if_missing = True):
        
        """
        Loads the class instance from disk.        
        
        Parameters
        ----------
        user_name : string (default None)
            If the user_name is not passed in then a default user should be
            defined in the config file.
        """
        
        #TODO: This should eventually have version lookup
        #https://docs.python.org/2/library/pickle.html#pickling-and-unpickling-normal-class-instances
        #would involve using __setstate__
        
        
        user_name = cls.resolve_user_name(user_name)       
        load_path = cls.get_file_path(user_name)
        
        #Handle potentially missing file
        #-------------------------------
        if not os.path.isfile(load_path):
            if create_if_missing:
                get_user_credentials_no_prompts()
            else:
                raise Exception('Requested token does not exist')
                       
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
                          
        return temp    

#%%

class ConfigUserInfo(object):
    
    def __init__(self,user_name):
        #TODO: populate this based on the config
        self.user_name_resolved = False
        self.user_name = None
        pass
    
        @staticmethod
    def resolve_user_name(user_name):
        """
        Parameters
        ----------
        user_name : string or None
            If the user_name is None, it is replaced with the default
            user from the configuration file.
        """
        if user_name is None:
            du = config.DefaultUser
            user_name = du.user_name
        elif user_name == '':
            raise Exception('specified user_name must be a non-empty string or None')
        else:
            if hasattr(config,'')
            pass
        #TODO: Look for user in config
            
        return user_name


  




class UserTokenRetriever(object):
    
    def __init__(self,user_info):
        #TODO: Include session
        self.user_info = user_info
        code  = self.get_authorization_code_auto(user_name, password)
        self.token = trade_code_for_user_access_token(code)

    def get_authorization_code_auto(self):  
        """
        The authorization code is what the user gives to the Client, allowing
        the Client to make requests on behalf of the User to Mendeley
    
        Rough OAUTH Outline
        -------------------
        1) User askes to use client (i.e. this code or an "app")
        2) Client gives User some information to give to Mendeley regarding
        the Client so that Mendeley can connnect the user to the Client.
        3) User gives the Client info to Mendeley along with user's id & pass, 
        and Mendeley gives the User some information (the authorization code) to 
        give to the Client.
        4) Client now has the information it needs to make requests for the 
        User's data. In most cases (although not this one) this would allow the
        User to never give it's Mendeley credentials to the client.
        
        """    
        
        URL = 'https://api-oauth2.mendeley.com/oauth/authorize'
        
        #STEP 1: Get form
        #----------------------------------------------
        payload = {
            'client_id'     : config.Oauth2Credentials.client_id,
            'redirect_uri'  : 'https://localhost', 
            'scope'         : 'all',
            'response_type' : 'code'}
        r = requests.get(URL, params=payload)
    
        if r.status_code != requests.codes.ok:
            raise Exception('TODO: Fix me, request failed ...')
            
        #STEP 2: Submit form for user authorizing client use
        #------------------------------------------------------
        payload2 = {
            'username' : self.user_info.user_name,
            'password' : self.user_info.password}
        r2 = requests.post(r.url,data=payload2,allow_redirects=False)    
        
        if r2.status_code != requests.codes.FOUND:
            raise Exception('TODO: Fix me, request failed ...')  
        
        #STEP 3: Grab code from redirect URL
        #----------------------------------------------
        parsed_url = requests.utils.urlparse(r2.headers['location'])
        
        #TODO: Update with response from StackOverflow    
        #instead of blindly grabbing the query
        #query => 'code=value'
        authorization_code = parsed_url.query[5:]
        
        return authorization_code

    def trade_code_for_user_access_token(self,code):
             
        """
        This method asks Mendeley for an access token given a user's code. This 
        code comes from the user telling Mendeley that this client 
        (identified by a Client ID) has permission to get information 
        from the user's account.
        
        I had wanted to replace the user input with just the code. Once I received
        the access token, I could then request the user's info. Unfortunately it
        seems that the default user informaton, particularly the user's email is
        no longer accessible unless the user has specified an email in 
        their profile.
        
        Parameters:
        -----------
        user: UserInfo
            This contains informaton about the user and can be obtained from:
            request_authorization_code.
    
        Returns:
        --------
        UserCredentials
            This token can be used to request information from the user's account.
            
        See Also:
        ---------
            
        
        """
        
        URL     = 'https://api-oauth2.mendeley.com/oauth/token'
        
        #TODO: This may or may not actually be needed
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        
        payload = {
            'grant_type'    : 'authorization_code',
            'code'          : code,
            'redirect_uri'  : config.Oauth2Credentials.redirect_url,
            'client_secret' : config.Oauth2Credentials.client_secret,
            'client_id'     : config.Oauth2Credentials.client_id,
            } 
    
        r = requests.post(URL,headers=headers,data=payload)
    
        if r.status_code != requests.codes.ok:
            raise Exception('TODO: Fix me, request failed ...')    
        
        return r.json()
            
class UserInfo(object):
    
    """
    This is a small little class that stores user info. The irony of such a
    class, one that holds onto the users password, given the goals OAuth,
    is not lost on me.    
    
    This class might be removed in favor of only using the authorization code.
    
    Previously I had used the profile methods to get a unique id but it seems
    like that function has changed :/ The use case I have in mind is someone
    that manually provides an authorization code. It would be nice to be able
    to automatically pull their information given this code, rather than
    have them provide it as well.
    
    Attributes
    ----------
    user_name : string
        The user_name is actually an email address.
    password : str
        The user's password.
    
    """
    def __init__(self,user_name,password):
        self.user_name = user_name
        self.password = password


class PublicCredentials(_Credentials):
    
    """
    TODO: Fill this out    
    
    """
        
    def __init__(self,session = None):
        self.populate_session(session)
        temp_json = self.create_initial_token()
        self.init_json_attributes(temp_json)

    def init_json_attributes(self,json):
        self.access_token = json['access_token']
        self.token_type = json['token_type']
        self.expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=json['expires_in'])
    
    def __repr__(self):
        return \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            '      expires : %s\n' % (str(self.expires))    + \
            'token_expired : %s\n' % (self.token_expired)
            
         

        
    @classmethod
    def load(cls,session=None):
        """
        Loads the class instance from disk.        
        
        """
   
        load_path = cls.get_file_path()
        
        if not os.path.isfile(load_path):
            raise Exception('Requested token does not exist')
                       
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
                        
        return temp        
    
    def renew_token(self):
        temp_json = self.create_initial_token()
        self.init_json_attributes(temp_json)
        self.save()
    
    @staticmethod   
    def create_initial_token():

        """
        Requests the client token from Mendeley. The results can then be
        used to construct OR update the object.
        
        See Also:
        ---------------
        get_public_credentials
        
        """
        URL = 'https://api-oauth2.mendeley.com/oauth/token'
  
        payload = {
            'grant_type'    : 'client_credentials',
            'scope'         : 'all',
            'redirect_uri'  : config.Oauth2Credentials.redirect_url,
            'client_secret' : config.Oauth2Credentials.client_secret,
            'client_id'     : config.Oauth2Credentials.client_id,
            }   
  
        r = requests.post(URL,data=payload)
        
        if r.status_code != requests.codes.ok:
            raise Exception('Request failed, TODO: Make error more explicit')
        
        return r.json()





  
