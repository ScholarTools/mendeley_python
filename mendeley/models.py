# -*- coding: utf-8 -*-
"""

Models:


"""

from .utils import get_truncated_display_string as td

"""
#This is temporary ...
class WTF(object):
    def __init__(self,json,m):
        import pdb
        pdb.set_trace()
        
class WTF2(object):
    def __init__(self,json,m,response_params):
        import pdb
        pdb.set_trace()    
"""

class ResponseObject(object):
    
    def __init__(self,json):
        self.json = json

    def __getattr__(self, name):
        if name in self.fields():
            return self.json.get(name)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    @classmethod
    def __dir__(cls):
        d = set(dir(cls) + cls.fields())
        d.remove('fields')

        return sorted(d)

    @classmethod
    def fields(cls):
        return []

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
    
def disciplines(json,m):
    """
    There is also a 'subdiscipline' field
    but it is always empty, I think this is a bug
    in the API
    """
    #'name
    #'subdisciplines'
    
    #return [x['name'] for x in json]
    return json
    
def document_types(json,m):
    
    return json

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
    
    
    def __init__(self,json,m,params):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.api._APIMethods
        """
        #TODO: build in next and prev support
        self.links = m.last_response.links
                
        fcn = params['fcn']
        #TODO: Figure out how to support lazy loading
        #TODO: Support view construction
        self.docs = [fcn(x,m) for x in json]
    
    #TODO: These will need to call some common function
    #That function will need to figure out how to call pages
    #outside of the typical function calls
    
    @classmethod
    def create(cls,json,m,params):
        
        #Callers
        #- catalog
        if isinstance(json,list):
            return DocumentSet(json,m,params)
        else:
            fcn = params['fcn']
            return fcn(json,m)
        
    def first_page(self):
        pass
    
    def next_page(self):
        pass
    
    def previous_page(self):
        pass
    
    def last_page(self):
        pass
      
    #def __repr__(self):
    #    pass

               
class Document(ResponseObject):
    
    def __init__(self,json,m):
        super(Document, self).__init__(json)
    
    @classmethod
    def fields(cls):
        return ['id','profile_id','source','title','type','year']
        
    def obj_fields(cls):
        return ['created','last_modified']
        
    def __repr__(self):
        return u'' + \
            '      created: %s\n' % self.created + \
            'last_modified: %s\n' % self.last_modified + \
            '           id: %s\n' % self.id

#???? How does this compare to 
class BibDocument(Document):

    def __init__(self,json,m):
        super(BibDocument, self).__init__(json,m)

    @classmethod
    def fields(cls):
        return super(BibDocument, self).fields() + \
            ['issue','pages','volume','websites']
            
    def __repr__(self):
        return super(BibDocument, self).__repr__() + \
            'issue: %s\n' + self.issue

class ClientDocument(Document):
    pass

class TagsDocument(Document):
    pass

class StatsDocument(Document):
    pass

class AllDocument(Document):
    pass

class CatalogDocument(object):
    """
    Attributes
    ----------
    
    """
    
    def __init__(self,json,m):
        """
        
        """
        self.raw = json
        
        self.title = json['title']        
        self.type = json['type']
        #Authors: To handle
        #   first_name
        #   last_name
        self.year = json['year']
        self.source = json['source']
        #Identifiers: To Handle      
        #   isbn?????
        #   pmid
        #   doi
        #   issn
        
        self.id = json['id']
        self.abstract = json.get('abstract')
        self.link = json['link']
        
    def __repr__(self):
        return u'' + \
           '   title: %s\n' % td(self.title) + \
           '    type: %s\n' % self.type + \
           '    year: %s\n' % self.year + \
           '  source: %s\n' % self.source + \
           '      id: %s\n' % self.id + \
           'abstract: %s\n' % td(self.abstract) + \
           '    link: %s\n' % td(self.link)
        
class BibCatalogDocument(CatalogDocument):

    def __init__(self,json,m):
        import pdb
        pdb.set_trace()
        super(BibCatalogDocument, self).__init__(json,m)
        self.issue = json['issue']
        self.pages = json['pages']
        self.volume = json['volume']
    
    def __repr__(self):
        return super(BibCatalogDocument,self).__repr__() + \
            '   issue: %s\n' % self.issue + \
            '   pages: %s\n' % self.pages + \
            '  volume: %s\n' % self.volume
        
class StatsCatalogDocument(CatalogDocument):
    
    def __init__(self,json,m):
        super(StatsCatalogDocument, self).__init__(json,m)
        self.group_count = json['group_count']
        self.reader_count = json['reader_count']
        
        #These are objects and not parsed
        #--------------------------------
        self.reader_count_by_academic_status = json['reader_count_by_academic_status']
        self.reader_count_by_country = json['reader_count_by_country']
        self.reader_count_by_discipline = json['reader_count_by_subdiscipline']
                   
class ClientCatalogDocument(CatalogDocument):

    def __init__(self,json,m):
        super(ClientCatalogDocument, self).__init__(json,m)  
        #file_attached: false

class AllCatalogDocument(CatalogDocument):
    
    def __init__(self,json,m):
        super(AllCatalogDocument, self).__init__()
        #TODO: Not yet implemented
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

class BibDocument(object):
    pass

class StatsDocument(object):
    pass

class ClientDocument(object):
    pass

class CatalogAllDocument(object):
    pass              
            
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
