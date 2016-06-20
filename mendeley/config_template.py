# -*- coding: utf-8 -*-
"""

This module stores user parameters. The _template
version is only meant as an example. A new user should
copy this version into "user_config.py" and fill in the values
as appropriate.

The "user_config.py" file is ignored from GIT commits so as to not be public

The "config_location" parameter can be used to specify a remote location from which
to load the config file.


"""

#If specified, this specifies that the config file should be loaded
#from the specified location. 
config_location = 'C:\users\my_mendeley_config.py'


# REQUIRED. This can be obtained from Mendeley.
#
#   http://dev.mendeley.com/
#
class Oauth2Credentials(object):
    client_secret = ''  # e.g. 'FfrRTSTasdfasdfasdfasdfsdfasdf3u'
    client_id = ''  # e.g. '200'
    redirect_url = 'https://localhost'


#-----------------------------------------------------------------
# Optional but recommended for personal methods
#
# If a user is not specified for the user credentials, 
# the default user (below) is used.
class DefaultUser(object):
    user_name = ''  # e.g. bob@smith.com
    password = ''  # e.g. 'password123'


# This is needed for the "other_users"
class User(object):
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

#-----------------------------------------------------------------
# Keys in the "other_user" dictionary are aliases for the user credentials.
#
# For example, you can request the 'testing' user and it will use
# the User credentials specified in the testing key.
#
#   Example: (Uncomment and modify to enable)
#   other_users = {'testing': User('jim@smith.com', 'my_testing_pass')}


#-----------------------------------------------------------------
# Fill this in to save the data in a location other than in:
#   <repo root>/data/
#
#   Example: (Uncomment and modify to enable)
#   default_save_path = 'C:/box_sync/mendeley_data'
