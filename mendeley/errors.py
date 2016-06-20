# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the mendeley_python package.
"""

class InvalidConfigError(Exception):
    pass

class OptionalLibraryError(Exception):
    pass

class DOINotFoundError(KeyError):
    pass

class CallFailedException(Exception):
    pass

class PDFError(Exception):
    pass

class AuthException(Exception):
    pass
