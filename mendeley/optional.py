# -*- coding: utf-8 -*-
"""
Handles importing of optional packages/modules. These imports are accomplished
normally unless they are missing. In that case a MissingModule is imported that
throws an error when you try and use it.

rr
pub_objects
"""

from .errors import OptionalLibraryError

class MissingModule(object):
    """
    This class throws an error upon trying to get an attribute.
    
    The idea is that if you import a missing module, and then try and get a
    class or function from this missing module (i.e. actually use the import
    calls) then an error is thrown.
    """
    def __init__(self,msg):
        self.msg = msg
        
    def __getattr__(self, name):
        #do we really want getattribute instead?
        #=> I think getattribute is more comprehensive
        raise OptionalLibraryError(self.msg)

#Optional import handling
#http://stackoverflow.com/a/563060/764365
try:
    import reference_resolver as rr
except ImportError:
    rr = MissingModule('The method called requires the library "reference_resolver" from the Scholar Tools Github repo')
    #TODO: Provide link to repo
    #Eventually pip the repo and specify pip is possible

try:
    import database as db
except ImportError:
    db = MissingModule('The method called requires the library "reference_resolver" from the Scholar Tools Github repo')

try:
    import pypub.publishers.pub_objects as pub_objects
except ImportError:
    pub_objects = MissingModule('The method called requires the library "pypub" from the Scholar Tools Github repo')

try:
    from pypub.data_transform import df_to_paper_info
except ImportError:
    df_to_paper_info = MissingModule('The method called requires the library "pypub" from the Scholar Tools Github repo')

