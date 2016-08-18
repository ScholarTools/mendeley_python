# Standard imports
import sys

# Third party imports
import nose

# Local imports
from mendeley import client_library

'''
Things to test:
    - Starting up (which I guess includes syncing?)
    - Checking for documents
    - Adding to library
    - Updating a file from a local copy
    - Syncing after making some changes
    - Getting the trash/deleted IDs (which happens during sync anyway)
'''


def test_startup():
    try:
        lib = client_library.UserLibrary()
    except Exception:
        assert False


if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__

    sys.path.append('database')

    result = nose.run(argv=[sys.argv[0], module_name, '-v'])
