# -*- coding: utf-8 -*-
"""

This module is meant to handle things related to authentication for the
Mendeley API.

The interface for this code is currently in flux. The main pieces of the code
are in place but I'm working on rearranging them.

TODO: Make sure that all calls necessary are exposed as method of this module,
not as methods of the classes

TODO: Tokens should be singletons by name

"""

import datetime
from . import config
import pickle
import os
import inspect

import requests
from requests.auth import AuthBase

#http://apidocs.mendeley.com/home/authentication


class _Credentials(AuthBase):
    
    """
    This is a superclass for:
    UserCredentials
    PublicCredentials
    
    TODO: I currently have a lot of duplicated code between the two classes that
    needs to be moved to here.
    """
    
    @staticmethod
    def get_save_base_path(create_folder_if_no_exist = False):
        #http://stackoverflow.com/questions/50499/in-python-how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executin/50905#50905
        package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))   
        
        #Go up to root, then down to specific save path
        root_path        = os.path.split(package_path)[0]
        save_folder_path = os.path.join(root_path, 'data', 'credentials')

        if create_folder_if_no_exist and not os.path.exists(save_folder_path):
            os.mkdir(save_folder_path)  
            
        return save_folder_path

class UserCredentials(_Credentials):
    
    """
    This class represents an access token. An access token allows a program to
    access user specific information. This class should normally be retrieved
    by:
    
    1) Calling UserCredentials.load(username)
    2) Calling get_access_token(username,password)
    
    Attributes:
    -------------------------------------------
    version : str
        The current version of the access token. Since these are saved to disk
        this value is retained
    username : str
    access_token : str
        The actual access token. This might be renamed ...
    token_type : str
        I'm not really sure what this is for. It is currently sent in response
        to a request for an access token but I'm not using it. Currently the 
        value is "bearer"
        
    JAH NOTE: I'm not thrilled with the name of this class ...
    """  
    
    
    #NYI: The goal is to say if the token will expire in 1 minute, renew it now 
    #rather than making a request and finding that the token has expired
    RENEW_TIME = datetime.timedelta(minutes = 1)    
    
    def __init__(self, json, user_info):
        self.version  = 1
        self.username = user_info.username
        
        self.populate_token_from_JSON(json)
             
    def populate_token_from_JSON(self, json):
        self.access_token  = json['access_token']
        self.token_type    = json['token_type']
        self.refresh_token = json['refresh_token']
        self.expires       = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'])
        
        return None


    def __repr__(self):
        
        #TODO: Make generic and make a call to the generic function (low priority)
        return \
            '      version : %d\n' % (self.version)         + \
            '     username : %s\n' % (self.username)        + \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            'refresh_token : %s\n' % (self.refresh_token)   + \
            '      expires : %s\n' % (str(self.expires))    + \
            ' token_expired: %s\n' % (self.token_expired)

    def __call__(self,r):
        
        """
        This method is called before a request is sent as part of inheriting from AuthBase
        
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
        time_diff = self.expires - datetime.datetime.now()
      
        return time_diff.total_seconds() < 0

    def renew_token_if_necessary(self):
      
        """
        Renews the access token if it about to or has expired.
      
      
        """
      
        if datetime.datetime.now() + self.RENEW_TIME > self.expires:
            self.renew_token()
        
        return None
      
      
    def renew_token(self):
      
        """
    
        Renews the access token so that requests can be made for user data.      
      
        NOTE: Apparently the refresh_token can be used even after it has expired.
        In this case the refresh token is like the access token in OAuth 1
        """      
      
        URL     = 'https://api-oauth2.mendeley.com/oauth/token'      
      
        client_auth = requests.auth.HTTPBasicAuth(
            config.Oauth2Credentials.client_id,
            config.Oauth2Credentials.client_secret)
        
        post_data = {"grant_type"   :   "refresh_token",
                     "refresh_token":   self.refresh_token}
                   
        r = requests.post(URL,auth=client_auth,data=post_data)
      
        if r.status_code != requests.codes.ok:
            raise Exception('TODO: Fix me, request failed ...')
      
        self.populate_token_from_JSON(r.json())
      
        self.save()
      
        return None
      
    @classmethod
    def get_file_path(cls,username,create_folder_if_no_exist = False):

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

        #Create a valid save name from the username (email)
        #----------------------------------------------------------------------
        #Good enough for now ... 
        #Removes periods from email addresses, leaves other characters
        save_name        = username.replace('.','') + '.pickle'

        save_folder_path = cls.get_save_base_path(create_folder_if_no_exist)
        
        final_save_path  = os.path.join(save_folder_path,save_name)
        
        return final_save_path        
        
    def save(self):
        
        """
        Saves the class instance to disk.
        """
        save_path = self.get_file_path(self.username, create_folder_if_no_exist = True)
        with open(save_path, "wb") as f:
            pickle.dump(self,f)
        return None
    
    @staticmethod
    def does_token_exist(username):
        pass
        #TODO: Allow user to see if the token exists
    
    @classmethod
    def load(cls, username = None):
        
        """
        Loads the class instance from disk.        
        
        Parameters
        ----------
        username : str
            If the username is not passed in then a default user should be
            defined in the config file.
        """

        

        #TODO: Do an explicit test for file existence (or catch and test)
        
        #TODO: This should have version lookup
        #https://docs.python.org/2/library/pickle.html#pickling-and-unpickling-normal-class-instances
        #would involve using __setstate__
        if username is None:
            du       = config.DefaultUser
            username = du.username
            
        load_path = cls.get_file_path(username)
        
        if not os.path.isfile(load_path):
            raise Exception('Requested token does not exist')
                
        
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
            
        #TODO: allow for getting new access token if needed    
            
        return temp    

#TODO: This will provide a URL for the user
def _get_authorization_code_manually():
    pass

def _get_authorization_code_auto(username,password):
    
    """
        
    
    Parameters:
    -----------
    username : str
    
    password : str
        
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
        'username' : username,
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
    
    user = UserInfo(username,password,authorization_code)    
    
    return user
 
#TODO: Finish this ...
def get_user_credentials_with_prompts(save=True):
    pass

 
def get_user_credentials_no_prompts(username, password, save=True):

    """
    This function returns an access token for accessing user information. It 
    does so without requiring any user prompts. As such it requires the user
    to enter their password into this function.    
    
    Parameters:
    -----------
    username : str
        The user name as prompted by Mendeley. This is usually the email
        address used to log into Mendeley.
    password : str
        The password associated with the account. This is currently only used 
        in order to get the access token.
        
    Returns
    -------
    UserCredentials
        This token can be used to request information from the user's account.
    
    """

    code  = _get_authorization_code_auto(username, password)
    token = trade_code_for_user_access_token(code)
    
    if save:
        token.save()
        
    return token

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
    class given OAuth is not lost on me.    
    
    This class might be removed in favor of only using the authorization code.
    
    Previously I had used the profile methods to get a unique id but it seems
    like that function has changed :/ The use case I have in mind is someone
    that manually provides an authorization code. It would be nice to be able
    to automatically pull their information given this code, rather than
    have them provide it as well.
    
    Attributes:
    ----------------------------------------
    username : str
        The username is actually an email address.
    password : str
        The user's password.
    authorization_code : str
        An authorizaton code given to the client when the user "authorizes" the
        client to have access to the user's account.
    
    """
    def __init__(self,username,password,authorization_code):
        self.username           = username
        self.password           = password
        self.authorization_code = authorization_code
        
    def getBasicAuth(self):
        """
        This turned out not to be needed. I'm leaving it in for now.
        """
        return requests.auth.HTTPBasicAuth(self.username,self.password)


class PublicCredentials(_Credentials):
    
    """
    TODO: Fill this out    
    
    """
    
    TOKEN_SAVE_NAME = 'client_auth.pickle'
    RENEW_TIME = datetime.timedelta(minutes = 1)      
    
    def __init__(self,json):
        
        self.access_token = json['access_token']
        self.token_type   = json['token_type']
        self.expires      = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'])
    
    def __repr__(self):
        
        #TODO: Make generic and make a call to the generic function
        return \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            '      expires : %s\n' % (str(self.expires))    + \
            ' token_expired: %s\n' % (self.token_expired)
    
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
        
        See Also:
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
      
        if datetime.datetime.now() + self.RENEW_TIME > self.expires:
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
            'redirect_uri'  : config.Oauth2Credentials.redirect_url,
            'client_secret' : config.Oauth2Credentials.client_secret,
            'client_id'     : config.Oauth2Credentials.client_id,
            }   
  
        r = requests.post(URL,data=payload)
        
        if r.status_code != requests.codes.ok:
            raise Exception('Request failed, TODO: Make error more explicit')
        
        return r.json()




def _get_public_credentials():

    """
    Get's credentials needed for making public requests. This is the 
    authentication info needed for the client.
    
    In general it is not necessary to call this function directly. Instead one
    should just call the Public Methods API Constructor.
    
    Returns:
    --------
    PublicCredentials
    
    See Also:
    .api.PublicMethods
    
    """
    
    if PublicCredentials.token_exists_on_disk():
        return PublicCredentials.load()
    else:
        r = PublicCredentials._make_request_for_token()
        
        pat = PublicCredentials(r)
    
        pat.save()    
    
        return pat
  
