# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the mendeley_python package.
"""

class InvalidConfig(Exception):
    pass

class OptionalLibraryError(Exception):
    pass


# ----------------- User Library Errors ----------------
class DOINotFoundError(KeyError):
    pass

class DocNotFoundError(KeyError):
    pass



class CallFailedException(Exception):
    pass

class PDFError(Exception):
    pass

class AuthException(Exception):
    pass


# ----------------- Database Errors --------------------
class MultipleDoiError(Exception):
    pass

class DatabaseError(Exception):
    pass
