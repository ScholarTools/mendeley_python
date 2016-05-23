# -*- coding: utf-8 -*-
"""

Models:

See Also
--------
mendeley.api => contains the code that makes requests for these models

"""

from collections import OrderedDict as ODict

from .utils import get_truncated_display_string as td
from .utils import get_list_class_display as cld

from . import utils

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


# %%

class ResponseObject(object):
    # I made this a property so that the user could change this processing
    # if they wanted. For example, this would allow the user to return authors
    # as just the raw json (from a document) rather than creating a list of
    # Persons
    object_fields = {}

    def __init__(self, json):
        self.json = json

    def __getattr__(self, name):

        # This check allows an optional field to be returned as None
        # even if it isn't in the current json definition
        #
        # This however still keeps in place errors like if you ask for:
        # document.yeear <= instead of year
        if name in self.fields():
            value = self.json.get(name)
            if value is None:
                return None
            elif name in self.object_fields:
                method_fh = self.object_fields[name]
                return method_fh(value)
            else:
                return value
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


# %%
class DocumentIdentifiers(ResponseObject):
    @classmethod
    def fields(cls):
        return ['pmid', 'issn', 'doi', 'isbn', 'arxiv']

    def _null(self):
        self.pmid = None
        self.issn = None
        self.doi = None
        self.isbn = None
        self.arxiv = None

    def __repr__(self):
        pv = ['pmid', self.pmid, 'doi', self.doi, 'issn', self.issn,
              'isbn', self.isbn, 'arxiv', self.arxiv]
        return utils.property_values_to_string(pv)


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
           'first_name: %s\n' % self.first_name + \
           'last_name: %s\n' % self.last_name


class Annotation(object):
    def __init__(self, json, m):
        import pdb
        pdb.set_trace()


# %%
def academic_statuses(json, m):
    """
    The json contains a list of dictionaries but each dictionary
    only contains a description key. So instead of returning the dictionaries
    I'm currently only returning the descriptions.
    """
    return [x['description'] for x in json]


def subject_areas(json, m):
    """
    There is also a 'subdiscipline' field
    but it is always empty, I think this is a bug
    in the API
    """
    # 'name
    # 'subdisciplines'

    # return [x['name'] for x in json]
    return json


def document_types(json, m):
    return json


def deleted_document_ids(json, m):
    """
    This is for the deleted_documents function.
    """
    return [x['id'] for x in json]


# %%

class ProfileInfo(object):
    """
    http://dev.mendeley.com/methods/#profile-attributes
    
    Attributes
    ----------    
    
    #TODO: Allow updating 
    """

    def __init__(self, json, m):
        """
        Parameters
        ----------
        json : dict
        m : api.UserMethods
        """

        # TODO: I'd like to eventually populate each attribute
        # lazily - TODO: Write code that writes this code
        for key in json:
            setattr(self, key, json[key])

    def __repr__(self):
        return \
            'first_name : %s\n' % (self.first_name) + \
            ' last_name : %s\n' % (self.last_name)


class DocumentSet(object):
    """
    Responsible for managing a set of documents.
    """

    def __init__(self, json, m, params):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.api._APIMethods
        
        
        """
        # TODO: build in next and prev support
        self.links = m.last_response.links
        self.api = m
        self.response_params = params

        fcn = params['fcn']

        # TODO: Figure out how to support lazy loading
        # TODO: Support view construction
        self.docs = [fcn(x, m) for x in json]
        self.view = params['view']

    # TODO: These will need to call some common function
    # That function will need to figure out how to call pages
    # outside of the typical function calls

    def __iter__(self):
        """
        
        """
        page = self
        while page:
            for single_doc in page.docs:
                yield single_doc

            page = page.next_page()

    @classmethod
    def create(cls, json, m, params):
        """
        I believe this distinction was made to distinguish between instances
        in which a set was required or instances in which by definition
        only a single document would be returned. 
        
        This however needs to be clarified.
        """

        if isinstance(json, list):
            return DocumentSet(json, m, params)
        else:
            fcn = params['fcn']
            return fcn(json, m)

    # TODO: We should probably include a navigation method, similar
    # to Page in mendeley.pagination

    def first_page(self):
        pass

    def next_page(self):
        if 'next' not in self.links:
            return None
        else:
            next_url = self.links['next']['url']
            return self.api.make_get_request(next_url, DocumentSet, None, self.response_params)

    def previous_page(self):
        pass

    def last_page(self):
        pass

    def __repr__(self):
        pv = ['links', self.links.keys(), 'docs', cld(self.docs), 'view', self.view]
        return utils.property_values_to_string(pv)


class DeletedDocument(ResponseObject):
    def __init__(self, json, m):
        super(DeletedDocument, self).__init__(json)

    def _null(self):
        self.id = None

    @classmethod
    def fields(cls):
        return ['id']

    def __repr__(self):
        return 'id: %s' % self.id


class File(ResponseObject):
    """

    """
    def __init__(self, json):
        super().__init__(self, json)


class CreatedDocument(object):
    """
    Manages return info after creating a single document.

    Includes a call to a method in API that adds a file
    to this document. So the user can end up with this
    object for a given document and uniquely add a file.

    """

    # TODO: implement method to add file.

    def __init__(self, json, m):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.api._APIMethods


        """
        self.api = m
        self.json = json
        self.doc_id = json['id']
        self.title = json['title']
        self.doi = json['identifiers']['doi']
        self.location = 'https://api.mendeley.com/documents/' + self.doc_id
        self.default_return_type = 'object'

    @classmethod
    def create(cls, json, m, params):
        """
        I believe this distinction was made to distinguish between instances
        in which a set was required or instances in which by definition
        only a single document would be returned.

        This however needs to be clarified.
        """
        return DocumentSet(json, m)

    def addfile(self, file):
        from .api import API

        base_url = 'https://api.mendeley.com'
        url = base_url + '/files'
        object_fh = LinkedFile

        # Get rid of spaces in filename
        filename = self.title.replace(' ', '_') + '.pdf'

        params = None

        # Set headers
        headers = dict()
        headers['Content-Type'] = 'application/pdf'
        headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        headers['Link'] = '<' + self.location + '>; rel="document"'

        return API.make_post_request(API(), url, object_fh, params, headers=headers, files=file)

    def __repr__(self):
        #pv = [self.json[key] for key in self.json.keys()]
        #return utils.property_values_to_string(pv)
        return u'' + \
            'Title: %s\n' % self.title + \
            'DOI: %s\n' % self.doi + \
            'Doc ID %s\n' % self.doc_id + \
            'Doc URL %s\n' % self.location


class LinkedFile(object):
    """
    Manages return info after linking a file to a doc.

    """

    def __init__(self, json, m):
        """
        Parameters
        ----------
        json : dict
        m : mendeley.models.CreatedDocument object

        """
        self.json = json
        self.title = json['file_name']
        self.file_id = json['id']
        self.doc_id = json['document_id']
        self.location = 'https://api.mendeley.com/files/' + self.file_id

    def __repr__(self):
        return u'' + \
            'Title: %s\n' % self.title + \
            'File ID %s\n' % self.file_id + \
            'File URL %s\n' % self.location + \
            'Doc ID %s\n' % self.doc_id

class Document(ResponseObject):
    """

    Possible methods to add:
    ------------------------
    update
    delete
    move_to_trash
    attach_file
    add_note
    
    
    
    Attributes
    ----------
    source : string
        Publication outlet, i.e. where the document was published.
    year
    identifiers : [DocumentIdentifiers]
    id : string
        Identifier (UUID) of the document. This identifier is set by the server 
        on create and it cannot be modified.
    type : string
        The type of the document. Supported types: journal, book, generic, 
        book_section, conference_proceedings, working_paper, report, web_page, 
        thesis, magazine_article, statute, patent, newspaper_article, 
        computer_program, hearing, television_broadcast, encyclopedia_article, 
        case, film, bill.
    created
    profile_id : string
        Profile id (UUID) of the Mendeley user that added the document to 
        the system.
    last_modified
    title : string
        Title of the document.
    authors : [Person]
    keywords : list
        List of author-supplied keywords for the document.
    abstract : string
    

    #TODO: Incorporate below into above ...
    group_id : string (Not always present)
        Group id (UUID) that the document belongs to.
    created : string
    last_modified : string
    
    
    authors :     
    """

    object_fields = {
        'authors': Person.initialize_array,
        'identifiers': DocumentIdentifiers}

    def __init__(self, json, m):
        super(Document, self).__init__(json)

    def _null(self):
        """
        TODO: Ask on SO about this, is there an alternative approach?
        It does expose tab completion in Spyder ...
        """
        self.source = None  #
        self.year = None  #
        self.identifiers = None
        self.id = None  #
        self.type = None  #
        self.created = None  #
        self.profile_id = None  #
        self.last_modified = None  #
        self.title = None  #
        self.authors = None  #
        self.keywords = None
        self.abstract = None  #

    @classmethod
    def fields(cls):
        return ['source', 'year', 'identifiers', 'id', 'type', 'created',
                'profile_id', 'last_modified', 'title', 'authors', 'keywords',
                'abstract']

    def __repr__(self, pv_only=False):
        # TODO: Set this up like it looks in Mendeley
        pv = ['profile_id', self.profile_id,
              'created', self.created,
              'last_modified', self.last_modified,
              'id', self.id,
              'type', self.type,
              'title', td(self.title),
              'authors', cld(self.authors),
              'source', self.source,
              'year', self.year,
              'abstract', td(self.abstract),
              'keywords', td("%s" % self.keywords),
              'identifiers', cld(self.identifiers)]
        if pv_only:
            return pv
        else:
            return utils.property_values_to_string(pv)


# ???? How does this compare to
class BibDocument(Document):
    def __init__(self, json, m):
        super(BibDocument, self).__init__(json, m)
        # s1 = set(json.keys())
        # s2 = set(Document.fields())
        # s1.difference_update(s2)

    def _null(self):
        self.issue = None  #
        self.pages = None  #
        self.volume = None  #
        self.websites = None  #

    @classmethod
    def fields(cls):
        return super(BibDocument, cls).fields() + \
               ['issue', 'pages', 'volume', 'websites']

    def __repr__(self):
        pv = (super(BibDocument, self).__repr__(pv_only=True) +
              ['issue', self.issue, 'pages', self.pages,
               'volume', self.volume, 'websites', td(self.websites)])

        return utils.property_values_to_string(pv)


class ClientDocument(Document):
    """
    Attributes
    ----------
    authored
    confirmed :
        Flag to identify whether the metadata of the document is correct after 
        it has been extracted from the PDF file.
        ???? Needs review or that the user has updated it since being added via pdf ?
    file_attached
    hidden :
        Does this mean that it has been excluded from Mendeley's catalog?
    read
    starred    
    
    """

    def __init__(self, json, m):
        super(ClientDocument, self).__init__(json, m)

    def _null(self):
        self.authored = None  #
        self.confirmed = None  #
        self.file_attached = None  #
        self.hidden = None  #
        self.read = None  #
        self.starred = None  #

    @classmethod
    def fields(cls):
        return (super(ClientDocument, cls).fields() +
                ['hidden', 'file_attached', 'authored', 'read', 'starred', 'confirmed'])

    def __repr__(self):
        pv = (super(ClientDocument, self).__repr__(pv_only=True) +
              ['hidden', self.hidden, 'file_attached', self.file_attached,
               'authored', self.authored, 'read', self.read,
               'starred', self.starred, 'confirmed', self.confirmed])

        return utils.property_values_to_string(pv)


class TagsDocument(Document):
    """
    Attributes
    ----------
    tags :
        The user contributed strings
    """

    def __init__(self, json, m):
        super(TagsDocument, self).__init__(json, m)

    def _null(self):
        self.tags = None  #

    @classmethod
    def fields(cls):
        return (super(TagsDocument, cls).fields() + ['tags'])

    def __repr__(self):
        pv = (super(TagsDocument, self).__repr__(pv_only=True) + ['tags', td(self.tags)])
        return utils.property_values_to_string(pv)


class AllDocument(Document):
    pass


class PatentDocument(Document):
    pass


# %%
"""
Catalog Documents
"""


class CatalogDocument(object):
    """
    
    TODOO: This id old and needs to up updated like
    Attributes
    ----------
    
    """

    def __init__(self, json, m):
        """
        
        """
        self.raw = json

        self.title = json['title']
        self.type = json['type']
        # Authors: To handle
        #   first_name
        #   last_name
        self.year = json['year']
        self.source = json['source']
        # Identifiers: To Handle
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
    def __init__(self, json, m):
        import pdb
        pdb.set_trace()
        super(BibCatalogDocument, self).__init__(json, m)
        self.issue = json['issue']
        self.pages = json['pages']
        self.volume = json['volume']

    def __repr__(self):
        return super(BibCatalogDocument, self).__repr__() + \
               '   issue: %s\n' % self.issue + \
               '   pages: %s\n' % self.pages + \
               '  volume: %s\n' % self.volume


class StatsCatalogDocument(CatalogDocument):
    def __init__(self, json, m):
        super(StatsCatalogDocument, self).__init__(json, m)
        self.group_count = json['group_count']
        self.reader_count = json['reader_count']

        # These are objects and not parsed
        # --------------------------------
        self.reader_count_by_academic_status = json['reader_count_by_academic_status']
        self.reader_count_by_country = json['reader_count_by_country']
        self.reader_count_by_discipline = json['reader_count_by_subdiscipline']


class ClientCatalogDocument(CatalogDocument):
    def __init__(self, json, m):
        super(ClientCatalogDocument, self).__init__(json, m)
        # file_attached: false


class AllCatalogDocument(CatalogDocument):
    def __init__(self, json, m):
        super(AllCatalogDocument, self).__init__()
        # TODO: Not yet implemented
        pass

# %%
