# -*- coding: utf-8 -*-
"""
Insert description here
"""

def assign_json(json_data, field_name, optional=True, default=None):
    
    """
    This function can be used to make an assignment
    """    
    
    if field_name in json_data:
        return json_data[field_name]
    elif optional:
        return default
    else:
        raise Exception("TODO: Fix me")