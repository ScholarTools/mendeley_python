# -*- coding: utf-8 -*-
"""
"""

class DOIStats(object):
    
    """
    This class should return inforation about DOIs.
    
    TODO: This class was thrown together from a few older files.
    The content of these files has been pasted here. One of these files
    wrote info to disk and the other loaded it from disk. This wouldn't be 
    necessary in the new version.
    https://github.com/ScholarTools/mendeley_python/issues/6
    """    
    
    def __init__(self,user_library,created_since=None):
        
        #import json
        #from datetime import datetime
        #from mendeley import client_library
        #user_library = client_library.UserLibrary(verbose=True)
        
        #Let's get only newer DOIs
        start_work_date = datetime.strptime('2014-03-01', '%Y-%m-%d')
        
        new_docs = user_library.docs[user_library.docs['created'] > start_work_date]
        
        dois = new_docs['doi'].tolist()
        
        with open('dois.txt', 'w') as outfile:
            json.dump(dois,outfile)
        
        from collections import Counter
        
        # Read in dois.txt and separate by commas
        f = open('dois.txt', 'r')
        dois = f.read().split(',')
        
        # Remove all "" elements
        dois = list(set(dois) - set(""))
        
        prefixes = []
        names = []
        
        for x in range(len(dois)):
            if dois[x][2:5] != '10.':
                continue
            prefixes.append(dois[x][2:9])
            names.append(dois[x][2:-1])
        
        # Count and return each unique prefix with the number of times it occurs
        p = Counter(prefixes)
        top = p.most_common(len(p))
        
        '''
        text = open('doi_to_provider.txt', 'a')
        for x in range(0, len(top)):
            text.write(str(top[x]))
            text.write('\n')
        '''
        
        
        # Create list of DOIs with each unique prefix represented once, in decreasing order of occurrence
        examples = []
        for x in range(len(p)):
            pre = top[x][0]
            for y in range(len(prefixes)):
                if pre == prefixes[y]:
                    examples.append(names[y])
                    break
        
        unique_prefixes = [x[0] for x in top]
        
        print(examples)
        
        '''
        for x in range(len(prefixes)):
            if prefixes[x] == '10.1002':
                print(names[x])
        '''
