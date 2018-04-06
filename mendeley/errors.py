# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the mendeley_python package.
"""

class InvalidConfig(Exception):
    pass

class OptionalLibraryError(Exception):
    pass

<<<<<<< HEAD
=======
class UnsupportedEntryTypeError(Exception):
    pass

>>>>>>> a454f3d2717b10f207860099d8466b8333988a38

# ----------------- User Library Errors ----------------
class DOINotFoundError(KeyError):
    pass

class DocNotFoundError(KeyError):
    pass

<<<<<<< HEAD

=======
class DuplicateDocumentError(Exception):
    pass
>>>>>>> a454f3d2717b10f207860099d8466b8333988a38

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
