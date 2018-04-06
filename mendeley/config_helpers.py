# -*- coding: utf-8 -*-
"""
"""

#Standard Library Imports
import os
import importlib.machinery #Python 3.3+

#Local Imports
#---------------------------------------------------------
from . import errors
# Can't use utils in this module - circular imports
#from . import utils
from mendeley.errors import *

try:
    from . import user_config as config
except ImportError:
    raise errors.InvalidConfig('user_config.py not found')
        
      
if hasattr(config,'config_location'):
    #In this case the config is really only a pointer to another config  
    config_location = config.config_location
    
    if not os.path.exists(config_location):
        raise InvalidConfig('Specified configuration path does not exist')
    
    loader = importlib.machinery.SourceFileLoader('config', config_location)    
    config = loader.load_module()
    
#-----------------------------------------------------------------

class Config(object):
    
    """
    Attributes
    ----------
    Oauth2Credentials : 
    DefaultUser : User
    
    """
    
    def __init__(self):
        
        #This initialization code also defines what we are looking for or not looking for
        if not hasattr(config,'Oauth2Credentials'):
            raise Exception('user_config.py requires a "Oauth2Credentials" class')
        
        self.Oauth2Credentials = config.Oauth2Credentials        
        
        if hasattr(config,'DefaultUser'):       
            self.default_user = User(config.DefaultUser)
            
        if hasattr(config,'default_save_path'):
            self.default_save_path = config.default_save_path
        
        if hasattr(config,'other_users'):
            self.other_users = config.other_users

        self.validate()
    
    def get_user(self,user_name):
        """
        Calling Forms
        -------------
        1) Returns default user
        self.get_user(None)
        
        2) Returns default user
        self.get_user("default")

        3) Returns user if specs can be found
        self.get_user(user_name)

        """

        if user_name is None:
            return self.default_user
        
        if user_name == 'default':
            return self.default_user
            
        if self.default_user.user_name == user_name:
            return self.default_user
            
        if not hasattr(self,'other_users'):
            raise Exception('Missing user and other_users is not specified in the config file')
            
        other_users = self.other_users
        
        if user_name not in other_users:
            raise Exception('other_users config parameter is missing the requested user name')
            
        user_data = other_users[user_name]
        
        return User(user_data)
    
    @property
    def has_default_user(self):
        return hasattr(config,'DefaultUser')
    
    @property
    def has_testing_user(self):
        if not hasattr(config,'other_users'):
            return False
        else:
            #Keys are aliases for the users accounts (others_users should be a dict)
            return 'testing' in config.other_users

    def validate(self):
        #Oauth2Credentials validation
        #----------------------------------------------------    

    
        auth_creds = self.Oauth2Credentials
        ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','client_secret')
        ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','client_id')
        ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','redirect_url')
        #TODO: can check that redirect url is valid    
        
        #   Optional Values
        #==========================================================================
        
        #   DefaultUser validation
        if hasattr(self,'DefaultUser'):
            du = self.DefaultUser
            ensure_present_and_not_empty(du,'DefaultUser','user_name')
            #TODO: Could check for an email (i.e. user name is typically an email)        
            ensure_present_and_not_empty(du,'DefaultUser','password')   
    
        #   default_save_path validation
        if hasattr(config,'default_save_path'):
            pass
            #TODO: Validate that the path exists

        self.Oauth2Credentials = config.Oauth2Credentials        
        
        if hasattr(config,'DefaultUser'):       
            self.default_user = User(config.DefaultUser)
            
        if hasattr(config,'default_save_path'):
            self.default_save_path = config.default_save_path
        else:
            self.default_save_path = None
        
        if hasattr(config,'other_users'):
            self.other_users = config.other_users

    # TODO: rewrite without using utils
    # Utils currently calls back into this class
    # so we want to avoid circular dependencies ...
    '''
    def __repr__(self):
        pv = ['Oauth2Credentials', cld(self.Oauth2Credentials), 
              'default_user', cld(getattr(self,'default_user',None)),
                'default_save_path',getattr(self,'default_save_path',None),
                'other_users',cld(getattr(self,'other_users',None))]
        return utils.property_values_to_string(pv)
    '''


def ensure_present_and_not_empty(obj_or_dict,name,key_or_attribute,none_is_ok=False):
    
    """
    Inputs
    ------
    obj_or_dict : object instance or dict
    name : string
        The name of the object or dict, for displaying if an error occurs
    key_or_attribute : string
        The entry in the object or dict to examine
    none_is_ok : bool (default False)
        If true a None value for the entry is ok
    """    
    
    if isinstance(obj_or_dict,dict):
        if key_or_attribute in obj_or_dict:
            value = obj_or_dict[key_or_attribute]
        else:
            raise InvalidConfig('%s is missing the entry %s, please fix the config file' % (name,key_or_attribute))
    else:
        if hasattr(obj_or_dict,key_or_attribute):
            value = getattr(obj_or_dict,key_or_attribute)
        else:
            raise InvalidConfig('%s is missing the entry %s, please fix the config file' % (name,key_or_attribute))
            
    
    if value is None:
        if none_is_ok:
            pass
        else:
            raise InvalidConfig('"%s" in %s was found to have none value which is not allowed, please fix the config file' % (key_or_attribute,name))
    elif len(value) == 0:
        raise InvalidConfig('"%s" in %s was found to be empty and needs to be filled in, please fix the config file' % (key_or_attribute,name))

class User(object):
    
    def __init__(self,config_default_user):
        #TODO: Allow variations on the User formats
            #e.g => (user_name,password) or list
            #e.g => JSON or YAML            
            #e.g. => currently a class
            #=> promote to a class        
        self.user_name = config_default_user.user_name
        self.password = config_default_user.password
