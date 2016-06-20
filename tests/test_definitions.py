# -*- coding: utf-8 -*-
"""
"""

import sys, os

sys.path.append('..')
from mendeley import API

def test_definitions():
    m = API(user_name='public')
    
    academic_statuses = m.definitions.academic_statuses()
    print('Retrieved academic statuses')
    
    subject_areas = m.definitions.subject_areas()
    print('Retrieved subject areas')

    document_types = m.definitions.document_types()
    print('Retrieved document types')

    
    print('Finished running "Definitions" tests')


if __name__ == '__main__':
    print('Running "Definitions" tests')
    test_definitions()