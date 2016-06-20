# -*- coding: utf-8 -*-
"""
"""

#TODO: Should build in forced renewals

import sys
sys.path.append('..')

from mendeley import auth
from mendeley import config

def test_auth():
    public_credentials = auth.retrieve_public_authorization()
    
    public_credentials.renew_token()

    default_credentials = auth.retrieve_user_authorization()
    
    default_credentials.renew_token()
    
    print(default_credentials)
    
    if config.has_default_user:
        testing_credentials = auth.retrieve_user_authorization(user_name='testing')
    else:
        print('Skipped missing testing user')
    
    print('Completed Authorization tests')
    
if __name__ == '__main__':
    print('Running "Auth" tests')
    test_auth()