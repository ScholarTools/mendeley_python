# -*- coding: utf-8 -*-
"""
"""

#TODO: Should build in forced renewals

import sys
sys.path.append('..')

from mendeley import auth

def test_auth():
    public_credentials = auth.retrieve_public_credentials()

    default_credentials = auth.retrieve_user_credentials()
    
    testing_credentials = auth.retrieve_user_credentials(user_name='testing')
    
if __name__ == '__main__':
    print('Running "Auth" tests')
    test_auth()