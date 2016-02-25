# -*- coding: utf-8 -*-
"""
"""

sys.path.append('..')

from mendeley import auth

def test_auth():
    public_credentials = auth.
    m = API(user_name='public')
    
    academic_statuses = m.definitions.academic_statuses()
    print('Retrieved academic statuses')
    
    disciplines = m.definitions.disciplines()
    print('Retrieved disciplines')

    document_types = m.definitions.document_types()
    print('Retrieved document types')

    
    print('Finished running "Definitions" tests')


if __name__ == '__main__':
    print('Running "Auth" tests')
    test_auth()