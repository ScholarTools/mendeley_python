# -*- coding: utf-8 -*-
"""

"""

import datetime
import requests
from requests.auth import AuthBase
from . import config
import pickle
import os, inspect

#http://apidocs.mendeley.com/home/authentication


#pyMendeley.auth.request_authorization_code
#TODO: This layout will likely change

#TODO: Move this to another module
#Goal was to have this function make API requests ...
class makeRequest():
    pass



class AccessToken(AuthBase):
    
    """
    This class represents an access token. An access token allows a program to
    access user specific information. This class should normally be retrieved
    by:
    
    1) Calling AccessToken.load(username)
    2) Calling get_access_token()
    
    Attributes:
    -------------------------------------------
    version : str
        The current version of the access token. Since these are saved to disk
        this value is retained
    """  
    
    
    #NOTE: Maybe this should be pulled from a user config ... ????
    RENEW_TIME = datetime.timedelta(minutes=5)    
    
    def __init__(self,json,user_info):
        self.version       = 1
        self.username      = user_info.username
        #self.password      = user_info.password
        
        self.populateTokenFromJSON(json)
             
    def populateTokenFromJSON(self,json):
        self.access_token  = json['access_token']
        self.token_type    = json['token_type']
        self.refresh_token = json['refresh_token']
        self.expires       = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'])
        
        return None

    def __call__(self,r):
        #Called before request is sent
          
        self.renewTokenIfNecessary()
        
        r.headers['Authorization'] =  "bearer " + self.access_token       
        
        return r    
    
      
    @property
    def token_expired(self):
        time_diff = self.expires - datetime.datetime.now()
      
        #I'm a bit surprised this isn't a @property ...
        return time_diff.total_seconds() < 0

    def renewTokenIfNecessary(self):
      
        """
         Renews the access token if it has expired.
      
      
        """
      
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
    def getFilePath(username):

        """
        mendeley.auth.getFilePath
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
        save_path = os.path.join(root_path,'user_auth',save_name)
        
        return save_path        
        
    def save(self):
        save_path = AccessToken.getFilePath(self.username)
        with open(save_path, "wb") as f:
            pickle.dump(self,f)
        return None
    
    @staticmethod
    def load(username = None):
        
        """
        Loads the class instance from disk.        
        
        Parameters
        ---------------------
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
            
        load_path = AccessToken.getFilePath(username)
        with open(load_path,'rb') as f:
            temp = pickle.load(f)
            
        #TODO: allow for getting new access token if needed    
            
        return temp    
            
class UserInfo(object):
    
    """
    This is a small little class that stores user info. The irony of such a
    class given OAuth is not lost on me.    
    
    Attributes:
    ----------------------------------------
    username : str
        The username is actually an email address.
    password : str
        The user's password.
    code : str
        An authorizaton code given to the client when the user "authorizes" the
        client to have access to the user's account.
    
    """
    def __init__(self,username,password,code):
        self.username = username;
        self.password = password;
        self.code     = code;
        
    def getBasicAuth(self):
        """
        This turned out not to be needed. I'm leaving it in for now.
        """
        return requests.auth.HTTPBasicAuth(self.username,self.password)

def request_authorization_code(username,password):
    
    URL = 'https://api-oauth2.mendeley.com/oauth/authorize'
    
    #STEP 1: Get form
    #----------------------------------------------
    #TODO: I think this step can be skipped    
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
    
    #TODO: Update with response from Slashdot    
    #instead of blindly grabbing the query
    #query => 'code=value'
    code = parsed_url.query[5:]
    
    user = UserInfo(username,password,code)    
    
    return user
  
"""
def get_access_token(username,password)
code  = auth.request_authorization_code(du.username,du.password)
token = auth.get_access_token(code)
#token.save()

"""
  
def code_for_token(user):
        
    #TODO: add autosave option here ...        
        
    """

    """
    
    URL     = 'https://api-oauth2.mendeley.com/oauth/token'
    
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    payload = {
        'grant_type'    : 'authorization_code',
        'code'          : user.code,
        'redirect_uri'  : 'https://localhost',
        'client_secret' : config.Oauth2Creds.client_secret,
        'client_id'     : config.Oauth2Creds.client_id,
        } 

    r = requests.post(URL,headers=headers,data=payload)

    if r.status_code != requests.codes.ok:
      raise Exception('TODO: Fix me, request failed ...')    
    
    return AccessToken(r.json(),user)