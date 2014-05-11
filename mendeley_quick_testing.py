# -*- coding: utf-8 -*-
"""

"""

from mendeley import auth
from mendeley import config
import mendeley.api

import pdb
#import mendeley

#auth.get_my_path()

#at = auth.AccessToken.load()

um = mendeley.api.UserMethods()
wtf = um.get_library_ids(items = 1)

pdb.set_trace()