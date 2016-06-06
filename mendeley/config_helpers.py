# -*- coding: utf-8 -*-
"""
"""

#JAH: We might want to support specifying a file that trys to load the config
#file by path
#
#This would allow specifying a synced config file 
#http://stackoverflow.com/a/19011259/764365

#TODO: Surround with a try catch
class InvalidConfig(Exception):
    pass

try:
    from . import config
except ImportError:
    raise InvalidConfig('config.py not found ')


def validate_config():
    #Oauth2Credentials validation
    #----------------------------------------------------    
    if not hasattr(config,'Oauth2Credentials'):
        raise Exception('config.py requires a "Oauth2Credentials" class')

    auth_creds = config.Oauth2Credentials
    ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','client_secret')
    ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','client_id')
    ensure_present_and_not_empty(auth_creds,'Oauth2Credentials','redirect_url')
    #TODO: can check that redirect url is valid    
    
    #   Optional Values
    #==========================================================================
    
    #   DefaultUser validation
    if hasattr(config,'DefaultUser'):
        du = config.DefaultUser
        ensure_present_and_not_empty(du,'DefaultUser','user_name')
        #TODO: Could check for an email        
        ensure_present_and_not_empty(du,'DefaultUser','password')   

    #   default_save_path validation
    if hasattr(config,'default_save_path'):
        pass
        #TODO: Validate that the path exists

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
    