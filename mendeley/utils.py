# -*- coding: utf-8 -*-
"""

"""

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
    majority of returned json repsonses contain optional ...
    """    
    
    if field_name in json_data:
        return json_data[field_name]
    elif optional:
        return default
    else:
        raise Exception("TODO: Fix me")