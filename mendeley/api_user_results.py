# -*- coding: utf-8 -*-
"""
This module contains the resulting objects created from API calls.

It's design is currently in flux and will likely change.
"""

from .utils import assign_json, get_unnasigned_json


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
        #This would require passing this in based on the request
        

class CatalogSearchResults(object):
    """
    @DOC: http://apidocs.mendeley.com/home/public-resources/search-terms
    """

    def __init__(self,json):
        pass
    




class UserDocumentEntry(object):
    pass
    
    """
    
    self.tags
    """
    
class DocumentEntry(object):
    pass
        
class PublicDocumentEntry(object):
    
    @staticmethod
    def createObject(json_data):
        doc_type = json_data['type']
        if doc_type is 'Journal Article':
            return PublicJournalArticle(json_data)
        else:
            raise Exception('Unhandled document type: %s' % doc_type)
        

class IDs(object):
    
    def __init__(self,json_data):
        
        self.doi = assign_json(json_data,'doi')

class JournalIDs(IDs):
    
    def __init__(self,json_data):

        def aj(field,json=json_data): return assign_json(json,field)        
        
        super(self.__class__,self).__init__(json_data)       
        
        self.pmid      = aj('pmid')
        
        #NOTE: This is in the public version but not exposed
        #in the local :/
        self.issn      = aj('issn')
        
        #TODO:
        #nihms_id
        #pmc_id        
        
        #TODO: Not sure of the name ...
        #arxiv_id  = aj('arxivid')
        
        self.unassigned_json = get_unnasigned_json(json_data,self)        
        
    def __repr__(self):
        return \
            'pmid: %s\n' % (self.pmid)  + \
            ' doi: %s\n' % (self.doi)   + \
            'issn: %s\n' % (self.issn)            
        
        
class JournalArticle(object):
    
    type = 'Journal Article'
    
    def __init__(self,json_data):
        
        def aj(field,json=json_data): return assign_json(json,field)         
        
        self.mendeley_url = aj('mendeley_url')
        self.uuid     = aj('uuid')
        self.title    = aj('title')
        self.journal  = aj('publication_outlet')
        self.year     = aj('year')
        self.volume   = aj('volume')
        self.issue    = aj('issue')
        self.pages    = aj('pages')
        self.abstract = aj('abstract')
        
        #Skipping
        
        #Apparently this is in the public papers as well
        #Are these from users personal papers or somewhere else?
        self.tags       = aj('tags')
        


        self.urls = aj('url')
        self.ids  = JournalIDs(json_data['identifiers'])


#TODO: Not sure how to do this ...       
class UserJournalArticle():
    pass
                
class PublicJournalArticle(JournalArticle):
    
    def __init__(self,json_data):
        super(self.__class__,self).__init__(json_data)

        def aj(field,json=json_data): return assign_json(json,field)
                    
        if self.tags is not None:
            self.tags_count = json_data['tags_counts']
        else:
            self.tags_count = None
        
        self.oa_journal = json_data['oa_journal']
        self.readership_stats = DocReadershipStats(json_data['stats'])
        self.unassigned_json = get_unnasigned_json(json_data,self)
        
        #TODO:
        #self.categories = aj('categories') #This should be a class
        #Example:
        #[35, 462, 23, 455, 25, 43, 27, 193, 331, 331]
        #
     
 
class DocReadershipStats(object):
    
    """
    Originally seen in 
    """    
    
    def __init__(self,json_data):
        self.n_readers  = json_data['readers']
        
        #NOTE: All of this stats info sounds like it should really 
        #be readership info ...        
        
        temp_discipline = json_data['discipline']
        if len(temp_discipline) != 0:
            self.by_discipline = [DisciplineReadershipStats(x) for x in temp_discipline]
        else:
            self.by_discipline = None

        
        temp_country    = json_data['country']
        if len(temp_country) != 0:
            self.by_country = [CountryReadershipStats(x) for x in temp_country]
        else:
            self.by_country = None
        
        
        temp_status     = json_data['status']
        if len(temp_status) != 0:
            self.by_status = [StatusReadershipStats(x) for x in temp_status]
        else:
            self.by_status = None

     
    #TODO: This should be done more like:
    #http://www.mendeley.com/catalog/one-gaba-two-acetylcholine-receptors-function-c-elegans-neuromuscular-junction/ 
    """
    def __repr__(self):
        return \
            '   id: %s\n' % (self.id)       + \
            'value: %s\n' % (self.value)    + \
            ' name: %s\n' % (self.name) 
    """

""" 
EXAMPLE
{u'discipline': [{u'id': 19, u'value': 100, u'name': u'Medicine'}], 
u'country': [], u'status': [{u'name': u'Other Professional', u'value': 100}],
 u'readers': 1}
"""
    
#TODO: This should probably be elsewhere
#I'd like to have this:
#- hold onto disciples
#- make periodic requests for new disciplines
#- handle conversions - value to name

class DisciplineManager():
    pass

 
class StatusReadershipStats(object):
    
    def __init__(self,json_data):
        self.name  = json_data['name']
        self.percentage = json_data['value']

    def __repr__(self):
        return \
            self.name + ': %d%%\n' % self.percentage
     
    def __str__(self):
        return self.__repr__()    
   
class CountryReadershipStats(object):
    
    def __init__(self,json_data):
        self.name  = json_data['name']
        self.percentage = json_data['value']

    def __repr__(self):
        return \
            self.name + ': %d%%\n' % self.percentage
     
    def __str__(self):
        return self.__repr__()
    
class DisciplineReadershipStats(object):

    """
    See Also:
    ---------
    DocReadershipStats
    """

    def __init__(self,json_data):
        self.id    = json_data['id']
        self.name  = json_data['name']
        self.percentage = json_data['value']

    def __repr__(self):
        return \
            self.name + ': %d%%\n' % self.percentage
     
    def __str__(self):
        return self.__repr__()

        
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
    