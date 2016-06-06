#TODO: Validate the config

from .config_helpers import validate_config

validate_config()

from .api import API



"""
Layout:
-------
api : main module for making calls
auth : module that handles signing requests (authentication)
models : 

"""