# -*- coding: utf-8 -*-
"""
#TODO: break out display utils to another module
"""

from . import config
import os
import inspect

def property_values_to_string(pv):
    """
    Parameters
    ----------
    pv : OrderedDict
        Keys are properties, values are values
    """

    #Max length    
    
    keys = pv[::2]
    values = pv[1::2]
    
    key_lengths = [len(x) for x in keys]
    max_key_length = max(key_lengths)
    space_padding = [max_key_length - x for x in key_lengths]
    key_display_strings = [' '*x + y for x,y in zip(space_padding,keys)]
    
    str = u''
    for (key,value) in zip(key_display_strings,values):
        str += '%s: %s\n' % (key,value)
        
    return str

def get_list_class_display(value):
    """
    TODO: Go from a list of objects to:
    [class name] len(#)
    """
    if value is None:
       return 'None'  
    elif isinstance(value,list):
        #Check for 0 length
        try:
            if len(value) == 0:
                return u'[??] len(0)'
            else:
                return u'[%s] len(%d)' % (value[0].__class__.__name__,len(value))
        except:
            import pdb
            pdb.set_trace()
        #run the code
    else:
        return u'<%s>' % (value.__class__.__name__)

def get_truncated_display_string(input_string,max_length = 30):
    if input_string is None:
        return 'None'
    elif len(input_string) > max_length:
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
    This function returns the location of the folder in which to save data
    for a given calling function.
    
    The default save location is:
        <repo root>/data
    
    This value can be overridden by placing the value 'default_save_path'
    in the config file.
    
    Parameters
    ----------
    sub_directories_list : string or list
    create_folder_if_no_exist : boolean
    
    """

    if not isinstance(sub_directories_list,list):
        #Assume string, normally I would check for a string but apparently this 
        #is a bit quirky with Python 2 vs 3
        sub_directories_list = [sub_directories_list]
  
    if hasattr(config,'default_save_path'):
        root_path = config.default_save_path
        if not os.path.isdir(root_path):
            raise Exception('Specified default save path does not exist')
    else:
        #http://stackoverflow.com/questions/50499/in-python-how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executin/50905#50905
        package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))   
        
        #Go up to root, then down to specific save path
        root_path = os.path.split(package_path)[0]
        root_path = os.path.join(root_path, 'data')
    
    
    save_folder_path = os.path.join(root_path, *sub_directories_list)

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