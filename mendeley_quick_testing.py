# -*- coding: utf-8 -*-
"""

"""

from mendeley import auth
from mendeley import api as mapi

import pdb

#1 Retrieval of a user token
#-----------------------------
#du = config.defaultUser
#wtf = auth.get_user_access_token_no_prompts(du.username,du.password)

#2 Loading a token from disk
#------------------------------
#NOTE: I'd like to expose load via a 
at = auth.UserAccessToken.load()

#3 Making a function call
#------------------------------
um  = mapi.UserMethods()
wtf = um.profile_get_info()
#wtf = um.get_library_ids(items = 1)

pdb.set_trace()





#pdb.set_trace()