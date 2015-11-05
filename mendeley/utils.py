# -*- coding: utf-8 -*-
"""

"""

import os
import inspect


def get_truncated_display_string(input_string,max_length = 30):
    if len(input_string) > max_length:
        return input_string[:max_length] + '...'
    else:
        return input_string

def user_name_to_file_name(user_name):
    """
    Provides a standard way of going from a user_name to something that will
    be unique (should be ...) for files
    
    NOTE: NO extensions are added

    See Also:
    utils.get_save_root
    """
    
    #Create a valid save name from the user_name (email)
    #----------------------------------------------------------------------
    #Good enough for now ... 
    #Removes periods from email addresses, leaves other characters
    return user_name.replace('.','')

def get_save_root(sub_directories_list,create_folder_if_no_exist=True):
    """
    We save things in the repo root in a data directory.
    
    NOTE: We could eventually change this by referencing a config file ...
    
    From there each part of the repo chooses where to save things relative to
    this base location.
    
    """

    if not isinstance(sub_directories_list,list):
        #Assume string, normally I would check for a string but apparently this 
        #is a bit quirky with Python 2 vs 3
        sub_directories_list = [sub_directories_list]
  
    #http://stackoverflow.com/questions/50499/in-python-how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executin/50905#50905
    package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))   
        
    #Go up to root, then down to specific save path
    root_path        = os.path.split(package_path)[0]
    save_folder_path = os.path.join(root_path, 'data', *sub_directories_list)

    if create_folder_if_no_exist and not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)  
            
    return save_folder_path

def get_unnasigned_json(json_data,populated_object):
    """
       Given an object which has had fields assigned to it, as well as the 
       JSON dict from which these values were retrieved, this function returns
       a list of keys that were not used for populating the object.
       
       In order to match the attribute names and dictionary keys must have the
       same names.
    """
    if len(json_data) == 0:
        return {}
    else:
        temp_keys = populated_object.__dict__.keys()
        return dict((key,json_data[key]) for key in set(json_data) if key not in temp_keys)

def assign_json(json_data, field_name, optional=True, default=None):
    
    """
    This function can be used to make an assignment to an object. Since the
    majority of returned json repsonses contain optional fields.
    """    
    
    if field_name in json_data:
        return json_data[field_name]
    elif optional:
        return default
    else:
        raise Exception("TODO: Fix me")