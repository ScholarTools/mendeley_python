# -*- coding: utf-8 -*-
"""

This module stores user parameters. The _template
version is only meant as an example. A new user should
copy this version into "config.py" and fill in the values
as appropriate.


"""

#Required. This can be obtained from Mendeley.
class Oauth2Creds(object):
    client_secret = ''
    client_id     = ''
    redirect_url  = ''
    
#Optional    
class defaultUser(object):
    username = ''
    password = ''