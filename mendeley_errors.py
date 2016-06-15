# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the mendeley_python package.
"""

#JAH: Why is this not in the package?

class OptionalLibraryError(Exception):
    pass

class DOINotFoundError(KeyError):
    pass

class CallFailedException(Exception):
    pass

class PDFError(Exception):
    pass
