# -*- coding: utf-8 -*-
"""
TODO: Move results objects into here
"""

from .utils import get_truncated_display_string as td

class WTF(object):
    def __init__(self,json,m):
        import pdb
        pdb.set_trace()    

class Annotation(object):
    
    def __init__(self,json,m):
        import pdb
        pdb.set_trace()

def academic_statuses(json,m):
    """
    The json contains a list of dictionaries but each dictionary
    only contains a description key. So instead of returning the dictionaries
    I'm currently only returning the descriptions.
    """
    return [x['description'] for x in json]

class ProfileInfo(object):
    
    """
    http://dev.mendeley.com/methods/#profile-attributes
    
    Attributes
    ----------    
    
    #TODO: Allow updating 
    """
    def __init__(self,json,m):
        
        """
        Parameters
        ----------
        json : dict
        m : api.UserMethods
        """
             
        #TODO: I'd like to eventually populate each attribute 
        #lazily - TODO: Write code that writes this code
        for key in json:
            setattr(self,key,json[key])

    def __repr__(self):
        
        return \
            'first_name : %s\n' % (self.first_name) +\
            ' last_name : %s\n' % (self.last_name)


class DocumentSet(object):
    
    def __init__(self,json,m):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.api._APIMethods
        """
        #TODO: build in next and prev support
        self.links = m.last_response.links
        
        
        #TODO: Figure out how to support lazy loading
        #TODO: Support view construction
        self.docs = [CoreDocument(x,m) for x in json]
    
    #TODO: These will need to call some common function
    #That function will need to figure out how to call pages
    #outside of the typical function calls
    def first_page(self):
        pass
    
    def next_page(self):
        pass
    
    def previous_page(self):
        pass
    
    def last_page(self):
        pass
      
    def __repr__(self):
        pass
        
#TODO: There are multiple views which should be suppported
#This would involve throwing a switch above
class CoreDocument(object):
    """
    Attributes
    ----------
    id : string
        Identifier (UUID) of the document. This identifier is set by the server 
        on create and it cannot be modified.
    type : string
        The type of the document. Supported types: journal, book, generic, 
        book_section, conference_proceedings, working_paper, report, web_page, 
        thesis, magazine_article, statute, patent, newspaper_article, 
        computer_program, hearing, television_broadcast, encyclopedia_article, 
        case, film, bill.
    title : string (Required)
        Title of the document.
    profile_id : string
        Profile id (UUID) of the Mendeley user that added the document to 
        the system.
    group_id : string (Not always present)
        Group id (UUID) that the document belongs to.
    created : string
    last_modified : string
    abstract : string (Not always present)
    source : string
        Publication outlet, i.e. where the document was published.
    authors : [Person]
    identifiers : [DocumentIdentifiers]
    keywords : string (Not always present)
        List of author-supplied keywords for the document.
    """
    def __init__(self,json,m):
        self.raw = json
        
        self.id = json['id']
        self.type = json['type']
        self.title = json['title']
        self.profile_id = json['profile_id']
        self.group_id = json.get('group_id')
        self.created = json['created']
        self.last_modified = json['last_modified']
        self.abstract = json.get('abstract')
        self.source = json['source']
        #self.authors = json['authors']
        #self.identifiers = json['identifiers']
        self.keywords = json.get('keywords')
        
        #for key in json:
        #    setattr(self,key,json[key])
     
     
    @property
    def authors(self):
        if 'authors' in self.raw:
            return [Person(x) for x in self.raw['authors']]
        else:
            return None
            
    @property
    def identifiers(self):
        if 'identifiers' in self.raw:
            return DocumentIdentifiers(self.raw['identifiers'])
        else:
            return None

    def __repr__(self):
        #Not yet finished
        return \
            '           id : %s\n' % (self.id) +\
            '         type : %s\n' % (self.type) +\
            '        title : %s\n' % td(self.title) +\
            '   profile_id : %s\n' % self.profile_id +\
            '     group_id : %s\n' % self.group_id +\
            '      created : %s\n' % self.created +\
            'last_modified : %s\n' % self.last_modified +\
            '     abstract : %s\n' % td(self.abstract) + \
            '       source : %s\n' % td(self.source)
            
            #TODO: For objects or none, have function
            #which displays size and object type or None
            
            
class DocumentIdentifiers(object):
    
    def __init__(self,json):
        pass        
    
class Person(object):
    """
    http://dev.mendeley.com/methods/?python#people
    #TODO: Check out slots for this ...
    """
    def __init__(self,json):
        self.first_name = json['first_name']
        self.last_name = json['last_name']
