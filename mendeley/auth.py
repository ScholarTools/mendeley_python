# -*- coding: utf-8 -*-
"""

This module is meant to handle things related to authentication for the
Mendeley API.

In general it is better to interact with the API directly, rather than
interacting with this module.




The interface for this code is currently in flux. The main pieces of the code
are in place but I'm working on rearranging them.

TODO: Make sure that all calls necessary are exposed as method of this module,
not as methods of the classes

TODO: Tokens should be singletons by name

Mendeley Authethentication Documentation:
http://apidocs.mendeley.com/home/authentication

Public functions of interest:
----------------------------------------
get_user_credentials_no_prompts()




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
    Loads public cre

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

"""
-------------------------------------------------------------------------------
Token creation methods.
"""

def get_user_credentials_no_prompts(user_name=None, password=None, save=True):

    """
    This function returns an access token for accessing user information. It 
    does so without requiring any user prompts. As such it requires the user
    to enter their password into this function OR Alternatively if the values 
    are not provided the code will attempt to load them from the config file.    
    
    Parameters:
    -----------
    user_name : str (default None)
        The user name as prompted by Mendeley. This is usually the email
        address used to log into Mendeley.
    password : str
        The password associated with the account. This is currently only used 
        in order to get the access token.
    save : boolean (default True)
        If true the credentials will be saved locally (to disk) for reuse
        at later times.
        
    Returns
    -------
    UserCredentials
        This token can be used to request information from the user's account.
    
    """
    
    if user_name is None:
        du = config.DefaultUser
        user_name = du.user_name
        password = du.password

    code  = _get_authorization_code_auto(user_name, password)
    token = trade_code_for_user_access_token(code)
    
    if save:
        token.save()
        
    return token

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
    """
    
    @staticmethod
    def get_save_base_path(create_folder_if_no_exist = False):
        """
        The API credentials are stored at:
        <repo_base_path>/data/credentials
        
        NOTE: Anything in the data folder is omitted from versioning using
        .gitignore
        """
        
        return utils.get_save_root(['credentials'],create_folder_if_no_exist)

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
    
    
    #The amount of time prior to token expiration that a request should be
    #made to renew the token. See self.renew_token_if_necessary()
    #I'm trying to avoid the following:
    # 1) check for valid token
    # 2) token becomes invalid
    # 3) request with invalid token
    #
    #Default value: check if there is less than 1 minute
    RENEW_TIME = datetime.timedelta(minutes = 1)    
    
    def __init__(self, json, user_info):
        """
        Parameters
        ----------
        json : dict
        user_info : UserInfo
            
        """
        self.version = 1
        self.user_name = user_info.user_name
        self.populate_token_from_JSON(json)
             
    def populate_token_from_JSON(self, json):
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
        
        #TODO: Make generic and make a call to the generic function (low priority)
        return \
            '      version : %d\n' % (self.version)         + \
            '    user_name : %s\n' % (self.user_name)       + \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            'refresh_token : %s\n' % (self.refresh_token)   + \
            '      expires : %s\n' % (str(self.expires))    + \
            'token_expired : %s\n' % (self.token_expired)

    def __call__(self,r):
        
        """
        This method is called before a request is sent as part of inheriting 
        from AuthBase.
        
        See Also:
        .api.UserMethods
        """
        #Called before request is sent
          
        self.renew_token_if_necessary()
        
        r.headers['Authorization'] = "bearer " + self.access_token
        
        return r    
    
      
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

        Returns
        -------
        None
        """
      
        if datetime.datetime.now(pytz.utc) + self.RENEW_TIME > self.expires:
            self.renew_token()
        
        return None
      
      
    def renew_token(self):
      
        """
        Renews the access token so that requests can be made for user data.      
      
        NOTE: The refresh_token can be used even after the access token has 
        expired.
        """      
      
        URL     = 'https://api-oauth2.mendeley.com/oauth/token'      
      
        client_auth = requests.auth.HTTPBasicAuth(
            config.Oauth2Credentials.client_id,
            config.Oauth2Credentials.client_secret)
        
        post_data = {"grant_type"   :   "refresh_token",
                     "refresh_token":   self.refresh_token}
                   
        r = requests.post(URL,auth=client_auth,data=post_data)
      
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
      
        self.populate_token_from_JSON(r.json())
      
        self.save()
      
        return None
      
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
        
    def save(self):
        
        """
        Saves the class instance to disk.
        """
        save_path = self.get_file_path(self.user_name, create_folder_if_no_exist = True)
        with open(save_path, "wb") as f:
            pickle.dump(self,f)
        return None
    
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
            
        return user_name
    
    @classmethod
    def does_token_exist(cls,user_name):
        load_path = cls.get_file_path(user_name)
        return os.path.isfile(load_path)
    
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

def _get_authorization_code_auto(user_name,password):
    
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
    
    Parameters
    ----------
    user_name : string
        This is typically an email address.
    password : string
        
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
        'username' : user_name,
        'password' : password}
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
    
    user = UserInfo(user_name,password,authorization_code)    
    
    return user
  


def trade_code_for_user_access_token(user):
             
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
        'code'          : user.authorization_code,
        'redirect_uri'  : config.Oauth2Credentials.redirect_url,
        'client_secret' : config.Oauth2Credentials.client_secret,
        'client_id'     : config.Oauth2Credentials.client_id,
        } 

    r = requests.post(URL,headers=headers,data=payload)

    if r.status_code != requests.codes.ok:
      raise Exception('TODO: Fix me, request failed ...')    
    
    return UserCredentials(r.json(),user)

            
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
    authorization_code : str
        An authorizaton code given to the client when the user "authorizes" the
        client to have access to the user's account.
    
    """
    def __init__(self,user_name,password,authorization_code):
        self.user_name           = user_name
        self.password           = password
        self.authorization_code = authorization_code
        
    def getBasicAuth(self):
        """
        This turned out not to be needed. I'm leaving it in for now.
        """
        return requests.auth.HTTPBasicAuth(self.user_name,self.password)


class PublicCredentials(_Credentials):
    
    """
    TODO: Fill this out    
    
    """
    
    TOKEN_SAVE_NAME = 'client_auth.pickle'
    RENEW_TIME = datetime.timedelta(minutes = 1)      
    
    def __init__(self,json):
        
        self.access_token = json['access_token']
        self.token_type = json['token_type']
        self.expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=json['expires_in'])
    
    def __repr__(self):
        return \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            '      expires : %s\n' % (str(self.expires))    + \
            'token_expired : %s\n' % (self.token_expired)
    
    @property
    def token_expired(self):
        
        """
        Determine if the token has expired. As of this writing
        the token expires 1 hour after being granted.
        """
        time_diff = self.expires - datetime.datetime.now()
      
        return time_diff.total_seconds() < 0
        
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
    def get_file_path(cls,create_folder_if_no_exist = False):

        """     
        Provides a consistent path to where this object can be saved and loaded
        from. Currently this path is located in a "user_auth" directory 
        that is at the same level as the "mendeley" package.  
        
        repo_base:
            - mendeley  - Mendeley package
            - user_auth - Directory for storing access info. This directory
                          is excluded from commits by the .gitignore file.
        
        Parameters:
        -----------
        #TODO
        
        Returns:
        -------
        str
                
        
        """

        save_folder_path = cls.get_save_base_path(create_folder_if_no_exist)
        
        final_save_path  = os.path.join(save_folder_path,cls.TOKEN_SAVE_NAME)
        
        return final_save_path      
     
    def renew_token_if_necessary(self):
      
        """
        Renews the access token if it about to or has expired.
        
        See Also:
        __call__
        """

        #TODO: It would be nice to have this in _Credentials
      
        if datetime.datetime.now(pytz.utc) + self.RENEW_TIME > self.expires:
            json = self._make_request_for_token()
            self.__init__(json)
            
        return None
    
    def save(self):
        
        """
        Saves the class instance to disk.
        """
        save_path = self.get_file_path(create_folder_if_no_exist = True)
        with open(save_path, "wb") as f:
            pickle.dump(self,f)
        return None
    
    @classmethod
    def token_exists_on_disk(cls):
        load_path = cls.get_file_path(create_folder_if_no_exist = False)
        return os.path.isfile(load_path)
    
    @classmethod
    def load(cls):
        
        """
        Loads the class instance from disk.        
        
        """

        
        load_path = cls.get_file_path()
        
        if not os.path.isfile(load_path):
            raise Exception('Requested token does not exist')
                
        
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
                        
        return temp        
    
    @staticmethod   
    def _make_request_for_token():

        """
        Requests the client token from Mendeley. The results can then be
        used to construct OR update the object.
        
        See Also:
        ---------------
        get_public_credentials
        
        """
        URL     = 'https://api-oauth2.mendeley.com/oauth/token'
  
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





  
