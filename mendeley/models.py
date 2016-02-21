# -*- coding: utf-8 -*-
"""

Models:

See Also
--------
mendeley.api => contains the code that makes requests for these models

"""

from .utils import get_truncated_display_string as td
from .utils import get_list_class_display as cld

"""
These objects are called with the following forms:
1)  (self,json,m)
2)  (self,json,m,response_params)

json : json response from the request
m : mendeley.api.API


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
        
        #This check allows an optional field to be returned as None
        #even if it isn't in the current json definition
        #
        #This however still keeps in place errors like if you ask for:
        #document.yeear <= instead of year
        if name in self.fields():
            if name in self.object_fields:
                method_fh = self.object_fields[name]
                return method_fh(self.json.get(name))
            else:
                return self.json.get(name)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    @classmethod
    def __dir__(cls):
        d = set(dir(cls) + cls.fields())
        d.remove('fields')
        d.remove('object_fields')

        return sorted(d)

    @classmethod
    def fields(cls):
        """
        This should be overloaded by the subclass.
        """
        return []
        
    @classmethod
    def object_fields(cls):
        """
        This should be overloaded by the subclass.
        """
        return []

class Annotation(object):
    
    def __init__(self,json,m):
        import pdb
        pdb.set_trace()

#%%
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

#%%

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
    """
    Responsible for managing a set of documents.
    """
    
    def __init__(self,json,m,params):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.api._APIMethods
        
        
        """
        #TODO: build in next and prev support
        self.links = m.last_response.links
        self.api = m
        self.response_params = params
                
        fcn = params['fcn']
        
        #TODO: Figure out how to support lazy loading
        #TODO: Support view construction
        self.docs = [fcn(x,m) for x in json]
        self.view = params['view']
    
    #TODO: These will need to call some common function
    #That function will need to figure out how to call pages
    #outside of the typical function calls
    
    @classmethod
    def create(cls,json,m,params):
        """
        I believe this distinction was made to distinguish between instances
        in which a set was required or instances in which by definition
        only a single document would be returned. 
        
        This however needs to be clarified.
        """

        if isinstance(json,list):
            return DocumentSet(json,m,params)
        else:
            fcn = params['fcn']
            return fcn(json,m)
        
    def first_page(self):
        pass
    
    def next_page(self):
        next_info = self.links['next']
        next_url = next_info['url']
        return self.api.make_get_request(next_url,DocumentSet,None,self.response_params)
    
    def previous_page(self):
        pass
    
    def last_page(self):
        pass
      
    def __repr__(self):
        #TODO: Include more ...
        return u'' + \
           '   links: %s\n' % self.links.keys()
           

               
class Document(ResponseObject):
    
    """
    Attributes
    ----------
    source
    year
    identifiers
    id : string
        Identifier (UUID) of the document. This identifier is set by the server 
        on create and it cannot be modified.
    type
    created
    profile_id
    last_modified
    title
    authors
    keywords
    abstract
    

    #TODO: Incorporate below into above ...        
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
        super(Document, self).__init__(json)
    
    def _null(self):
        """
        TODO: Ask on SO about this, is there an alternative approach?
        It does expose tab completion in Spyder ...
        """
        self.source = None
        self.year = None
        self.identifiers = None
        self.id = None
        self.type = None
        self.created = None
        self.profile_id = None
        self.last_modified = None
        self.title = None
        self.authors = None
        self.keywords = None
        self.abstract = None
    
    @classmethod
    def fields(cls):
        return ['source', 'year', 'identifiers', 'id', 'type', 'created', 
        'profile_id', 'last_modified', 'title', 'authors', 'keywords', 
        'abstract']
        
    @property
    def object_fields(self):
        return {'authors':Person.initialize_array}
                
    def __repr__(self):
        #TODO: Set this up like it looks in Mendeley
        return u'' + \
            '      created: %s\n' % self.created + \
            'last_modified: %s\n' % self.last_modified + \
            '           id: %s\n' % self.id + \
            '         type: $s\n' % self.type + \
            '        title: %s\n' % td(self.title) \
            '      authors: %s\n' % cld(self.authors) #TODO: Might instead create a representation string like Smith & Lee or Smith et al. (Lee)
            '

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

#%%
"""
Catalog Documents
"""

class CatalogDocument(object):
    """
    
    TODOO: This id old and needs to up updated like
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

    **OLD**
    This will be deleted once I incorporate it into "Document" above    
    
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

#%%
            
class DocumentIdentifiers(object):
    
    def __init__(self,json):
        pass        
    
class Person(ResponseObject):
    """
    """
    @classmethod
    def fields(cls):
        return ['first_name', 'last_name']
    
    def _null(self):
        self.first_name = None
        self.last_name = None
     
    def initialize_array(json):
        return [Person(x) for x in json]
    
    def __repr__(self):
        return u'' + \
            'first_name: %s\n' % self.created + \
            ' last_name: %s\n' % self.last_modified + \
