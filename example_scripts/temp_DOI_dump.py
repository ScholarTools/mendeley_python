# -*- coding: utf-8 -*-
"""
TODO: Move to examples and document
"""

import json
from datetime import datetime

from mendeley import client_library

temp = client_library.UserLibrary(verbose=True)

#Let's get only newer DOIs
start_work_date = datetime.strptime('2014-03-01', '%Y-%m-%d')

new_docs = temp.docs[temp.docs['created'] > start_work_date]

dois = new_docs['doi'].tolist()

with open('dois.txt', 'w') as outfile:
    json.dump(dois,outfile)