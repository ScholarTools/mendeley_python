# -*- coding: utf-8 -*-
"""
Insert description here
"""

from .utils import assign_json

class TopAuthor(object):
    
    """
    See more information on this object at:
    @DOC: http://apidocs.mendeley.com/home/public-resources/stats-authors
    
    I've posted some questions there which may or may not ever get answered :/
    """
    def __init__(self,json):
        self.name  = json['name']
        self.value = json['value']
        #?? - do we want to know the discipline as well????
        
        
class LibraryResponse(object):
    
    """
    
    Response from:
    http://apidocs.mendeley.com/home/user-specific-methods/user-library
    
    Attributes:
    ---------------------------------------------
    
    
    """
    
    def __init__(self,json):
        self.document_ids   = json['document_ids']
        self.documents      = json['documents']
            #Contains:
            #  - id
            #  - version         
        
        self.total_results  = json['total_results']
        self.current_page   = json['current_page']
        self.total_pages    = json['total_pages']
        self.items_per_page = json['items_per_page']
        
#Will hold off on for now ...
#class LibraryIDHolder(object):
    
class ProfileInfo(object):
    
    def __init__(self,json):
        self.main    = ProfileMain(json['main'])
        self.awards  = ProfileAwards(json['awards'])
        self.cv      = ProfileCV(json['cv'])
        self.contact = ProfileContact(json['contact'])
        

class ProfileMain(object):
    
    def __init__(self,json):
                
        def aj(field,optional,json=json): return assign_json(json,field,optional)   
        
        self.academic_status_id = aj('academic_status_id',True) #Enumeration ??optional??
        #5 - Ph.D. Student     
        self.academic_status = aj('academic_status',True)
        self.bio             = aj('bio',False)
        self.discipline_id   = aj('discipline_id',True) #Enumeration ??optional??
        #3 - Biological Sciences
        self.discipline_name = aj('discipline_name',True) #??? optional???
        self.joined_date     = aj('joined',False)
        self.last_synced     = aj('last_synced',False)
        self.location        = aj('location', True) #??? optional???
        self.name            = aj('name',False)
        self.photo_url       = aj('photo',True)
        self.profile_id      = aj('profile_id',False)
        self.research_interests = aj('research_interests',True) #??? optional
        self.url             = aj('url',False)

        pass
    
    def __repr__(self):
        
        return \
            'academic_status_id: %s\n' % (self.academic_status_id)  + \
            '   academic_status: %s\n' % (self.academic_status)     + \
            '               bio: %s\n' % (self.bio)                 + \
            '     discipline_id: %s\n' % (self.discipline_id)       + \
            '   discipline_name: %s\n' % (self.discipline_name)     + \
            '       joined_date: %s\n' % (self.joined_date)         + \
            '       last_synced: %s\n' % (self.last_synced)         + \
            '          location: %s\n' % (self.location)            + \
            '              name: %s\n' % (self.name)                + \
            '         photo_url: %s\n' % (self.photo_url)           + \
            '        profile_id: %s\n' % (self.profile_id)          + \
            'research_interests: %s\n' % (self.research_interests)  + \
            '               url: %s\n' % (self.url)

class ProfileAwards(object):
    
    def __init__(self,json):
        pass

class ProfileCV(object):
    
    def __init__(self,json):
        pass

class ProfileContact(object):
    
    """
    Attributes:
    -----------
    address : str (optional)
        ???? No idea what the format of this is ...
    email : str (optional)

    """
    def __init__(self,json):
        
        def aj(field,json=json): return assign_json(json,field)        
        
        self.address = aj('address')
        self.email   = aj('email')
        self.im      = aj('im')
        self.fax     = aj('fax')
        self.mobile  = aj('mobile') 
        self.phone   = aj('phone')
        self.webpage = aj('webpage')
        self.zipcode = aj('zipcode')         

    def __repr__(self):
        
        return \
            'address: %s\n' % (self.address)  + \
            '  email: %s\n' % (self.email)    + \
            '     im: %s\n' % (self.im)       + \
            '    fax: %s\n' % (self.fax)      + \
            ' mobile: %s\n' % (self.mobile)   + \
            '  phone: %s\n' % (self.phone)    + \
            'webpage: %s\n' % (self.webpage)  + \
            'zipcode: %s\n' % (self.zipcode)
    