# -*- coding: utf-8 -*-
"""

This module is meant to handle things related to authentication for the
Mendeley API. Currently only private authentication is supported.


"""

import datetime
import requests
from requests.auth import AuthBase
from . import config
import pickle
import os, inspect

#http://apidocs.mendeley.com/home/authentication

class UserAccessToken(AuthBase):
    
    """
    This class represents an access token. An access token allows a program to
    access user specific information. This class should normally be retrieved
    by:
    
    1) Calling UserAccessToken.load(username)
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
    
    def __init__(self,json,user_info):
        self.version       = 1
        self.username      = user_info.username
        
        self.populateTokenFromJSON(json)
             
    def populateTokenFromJSON(self,json):
        self.access_token  = json['access_token']
        self.token_type    = json['token_type']
        self.refresh_token = json['refresh_token']
        self.expires       = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'])
        
        return None


    def __repr__(self):
        
        #TODO: Make generic and make a call to the generic function
        return \
            '      version : %d\n' % (self.version)         + \
            '     username : %s\n' % (self.username)        + \
            '  acess_token : %s\n' % (self.access_token)    + \
            '   token_type : %s\n' % (self.token_type)      + \
            'refresh_token : %s\n' % (self.refresh_token)   + \
            '      expires : %s\n' % (str(self.expires))

    def __call__(self,r):
        
        """
        This method is called before a request is sent.
        
        See Also:
        .api.UserMethods
        """
        #Called before request is sent
          
        self.renewTokenIfNecessary()
        
        r.headers['Authorization'] =  "bearer " + self.access_token       
        
        return r    
    
      
    @property
    def token_expired(self):
        
        """
        Determine if the token has expired. As of this writing
        the token expires 1 hour after being granted.
        """
        time_diff = self.expires - datetime.datetime.now()
      
        return time_diff.total_seconds() < 0

    def renewTokenIfNecessary(self):
      
        """
        Renews the access token if it about to or has expired.
      
      
        """
      
        #TODO: Replace with some buffer so that the request goes through
        if self.token_expired:
            self.renewToken()
        
        return None
      
      
    def renewToken(self):
      
        """
    
        Renews the access token so that requests can be made for user data.      
      
        NOTE: Apparently the refresh_token can be used even after it has expired.
        In this case the refresh token is like the access token in OAuth 1
        """      
      
        URL     = 'https://api-oauth2.mendeley.com/oauth/token'      
      
        client_auth = requests.auth.HTTPBasicAuth(
            config.Oauth2Creds.client_id,
            config.Oauth2Creds.client_secret)
        
        post_data = {"grant_type"   :   "refresh_token",
                     "refresh_token":   self.refresh_token}
                   
        r = requests.post(URL,auth=client_auth,data=post_data)
      
        if r.status_code != requests.codes.ok:
            raise Exception('TODO: Fix me, request failed ...')
      
        self.populateTokenFromJSON(r.json())
      
        self.save()
      
        return None
      
    @staticmethod
    def getFilePath(username,create_folder_if_no_exist = False):

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
        save_name = username.replace('.','') + '.pickle'

        #http://stackoverflow.com/questions/50499/in-python-how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executin/50905#50905
        package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))   
        
        #Go up to root, then down to specific save path
        root_path = os.path.split(package_path)[0]
        save_folder_path = os.path.join(root_path,'user_auth')

        if create_folder_if_no_exist and not os.path.exists(save_folder_path):
            os.mkdir(save_folder_path)
        
        final_save_path = os.path.join(save_folder_path,save_name)
        
        return final_save_path        
        
    def save(self):
        
        """
        Saves the class instance to disk.
        """
        save_path = self.getFilePath(self.username, create_folder_if_no_exist = True)
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
            du       = config.defaultUser
            username = du.username
            
        load_path = cls.getFilePath(username)
        
        if not os.path.isfile(load_path):
            raise Exception('Requested token does not exist')
                
        
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
            
        #TODO: allow for getting new access token if needed    
            
        return temp    
            
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

#TODO: This will provide a URL for the user
def get_authorization_code_manually():
    pass

    


def get_authorization_code_auto(username,password):
    
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
        'client_id'     : config.Oauth2Creds.client_id, 
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
def get_user_access_token_with_prompts(save_token = True):
    pass

 
def get_user_access_token_no_prompts(username,password,save_token = True):

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
    UserAccessToken
        This token can be used to request information from the user's account.
    
    """

    code  = get_authorization_code_auto(username,password)
    token = trade_code_for_user_access_token(code)
    
    if save_token:
        token.save()
        
    return token
  

class PublicAccessToken(object):
    
    """
    TODO: Fill this out    
    
    """
    
    def __init__(self,json):
        self.access_token = json['access_token']
        self.token_type   = json['token_type']
        self.expires_in   = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'])
        
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
          
        self.renewTokenIfNecessary()
        
        r.headers['Authorization'] =  "bearer " + self.access_token       
        
        return r        
     
    def renewTokenIfNecessary(self):
      
        """
        Renews the access token if it about to or has expired.
      
      
        """
      
              
        #TODO: I'm not sure how best to do this ...
        #Perhaps move the request into here, and have the method:
    # get_public_token just call the helper function ...
      
        #TODO: Replace with some buffer so that the request goes through
        if self.token_expired:
            pass
        
        return None
        
    def _make_request_for_token():
         pass
     
         #TODO: Move logic from function here ...
        
        
        

def get_public_credentials():

    """
        Get's information needed for making public requests
    """
    
    URL     = 'https://api-oauth2.mendeley.com/oauth/token'
  
    payload = {
        'grant_type'    : 'client_credentials',
        'redirect_uri'  : config.Oauth2Creds.redirect_url,
        'client_secret' : config.Oauth2Creds.client_secret,
        'client_id'     : config.Oauth2Creds.client_id,
        }   
  
    r = requests.post(URL,data=payload)
  
    import pdb
    pdb.set_trace()
  
def trade_code_for_user_access_token(user):
             
    """
    
    TODO: If everything is successful, the code itself should be sufficient
    at this point. User information can be gathered from requests.

    This method asks Mendeley for an access token given a code. This code comes
    from the user telling Mendeley that this client (identified by a Client ID)
    has permission to get information from the user.
    
    Parameters:
    -----------
    user: UserInfo
        This contains informaton about the user and can be obtained from:
        request_authorization_code.

    Returns:
    --------
    UserAccessToken
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
        'redirect_uri'  : config.Oauth2Creds.redirect_url,
        'client_secret' : config.Oauth2Creds.client_secret,
        'client_id'     : config.Oauth2Creds.client_id,
        } 

    r = requests.post(URL,headers=headers,data=payload)

    if r.status_code != requests.codes.ok:
      raise Exception('TODO: Fix me, request failed ...')    
    
    return UserAccessToken(r.json(),user)