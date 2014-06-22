# -*- coding: utf-8 -*-
"""
The goal of this code is to support hosting a client library. This module
should in the end function similarly to the Mendeley Desktop.

Tasks:
- sync documents
- add entries
- expose the li

Examples of others:
https://github.com/Mendeley/mendeley-oapi-example/blob/master/mendeley_client.py
https://github.com/Mendeley/mendeley-oapi-example/blob/master/synced_client.py
https://github.com/Mendeley/mendeley-api-python-example/blob/master/mendeley-example.py

"""

class UserLibrary():
    pass

    #This is the one I would like to interface with DJANGO

class UserClient():
    
    """ 
    Attributes:
    -----------
    library
    public_api?
    
    """    
    
    def __init__(self, user_name=None):
        pass
    

        #self
    
    def get_credentials():
        """
        If for some reason the user name is not recognized or available,
        provide prompts that help remedy this problem
        """
        pass