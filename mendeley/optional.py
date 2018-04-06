# -*- coding: utf-8 -*-
"""
Handles importing of optional packages/modules. These imports are accomplished
normally unless they are missing. In that case a MissingModule is imported that
throws an error when you try and use it.

<<<<<<< HEAD
TODO: document all optional imports

=======
>>>>>>> a454f3d2717b10f207860099d8466b8333988a38
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
    # TODO: Provide link to repo
    # Eventually pip the repo and specify pip is possible

<<<<<<< HEAD

try:
    from library_db import db_logging as db
except ImportError:
    db = MissingModule('The method called requires the library "ST_library_db" from the Scholar Tools Github repo')


=======
>>>>>>> a454f3d2717b10f207860099d8466b8333988a38
try:
    import pypub.publishers.pub_objects as pub_objects
except ImportError:
    pub_objects = MissingModule('The method called requires the library "pypub" from the Scholar Tools Github repo')

try:
    from pypub.paper_info import PaperInfo
except ImportError:
    PaperInfo = MissingModule('The method called requires the library "pypub" from the Scholar Tools Github repo')

try:
    from pypub.scrapers import base_objects
except ImportError:
    base_objects = MissingModule('The method called requires the library "pypub" from the Scholar Tools Github repo')

try:
    from scopy import Scopus
except ImportError:
    Scopus = MissingModule('The method called requires the library "scopy" from the Scholar Tools Github repo')

try:
    from pdfetch import pdf_retrieval
except ImportError:
    pdf_retrieval = MissingModule('The method called requires the library "pdfetch" from the Scholar Tools Github repo')
