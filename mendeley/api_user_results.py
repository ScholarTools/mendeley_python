# -*- coding: utf-8 -*-
"""
This module contains the resulting objects created from API calls.

It's design is currently in flux and will likely change.
"""

from . import api_results_analysis as analysis

from datetime import datetime
import inspect
import os
import pickle

from .utils import assign_json, get_unnasigned_json


def _get_save_base_path(api_object, create_folder_if_no_exist=True):

    """
        Return where to save user results based on the user and whether or not
        the private or public authorization is being used.
        
        This function is currently unfinished
    """
    #Public - error not yet implemented

    import pdb
    pdb.set_trace()

    #Private -
    package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    #Go up to root, then down to specific save path
    root_path        = os.path.split(package_path)[0]
    save_folder_path = os.path.join(root_path, 'data', 'credentials')

    if create_folder_if_no_exist and not os.path.exists(save_folder_path):
        os.mkdir(save_folder_path)

    return save_folder_path


    pass


        

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
        

        

class EntryIDs(object):
    
    def __init__(self,json_data):
        
        self.doi = assign_json(json_data,'doi')

class JournalIDs(EntryIDs):
    
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
    
    """
    Created by:
    
    This class is currently in development
    """
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

        
class LibraryIDs(object):
    
    """
    
    Response from:
    http://apidocs.mendeley.com/home/user-specific-methods/user-library
    AND
    .api.UserMethods.docs_get_library_ids    
    
    Attributes:
    -----------
    created_date : datetime
    document_ids : list
    document_versions : list
    n_entries_total : number
    current_page : number
    n_pages : number
    items_per_page : number
    is_all_ids : bool
        Indicates that the object contains all ids.
    """
    
    def __init__(self, json, user_api):
        self.created_date      = datetime.now()
        self.document_ids      = [x['id'] for x in json['documents']]
        self.document_versions = [x['version'] for x in json['documents']]       
        self.n_entries_in_lib   = json['total_results']
        self.current_page      = json['current_page']
        self.n_pages       = json['total_pages']
        self.items_per_page    = json['items_per_page']
        self._user_api         = user_api   
        #TODO: Do I want a 'is full' attribute that indicates all values have been saved????

    @property    
    def is_all_ids(self):
        return self.items_per_page >= self.n_entries_in_lib  
    
    def __repr__(self):
        return \
        '     created_date: %s\n' % (str(self.created_date)) + \
        ' n_entries_in_lib: %d\n' % (self.n_entries_in_lib)     + \
        '     current_page: %d\n' % (self.current_page)      + \
        '          n_pages: %d\n' % (self.n_pages)       + \
        '   items_per_page: %d\n' % (self.items_per_page)    + \
        '     document_ids: [1 x %d] List\n' % (len(self.document_ids)) + \
        'document_versions: [1 x %d] List\n' % (len(self.document_versions)) + \
        '       is_all_ids: %s\n' % (self.is_all_ids)
        
    def get_doc_details(self,index):

        """

        Parameters:
        -----------
        index: 
            0 based. 
        """        
        
        doc_method = self._user_api.docs_get_details 
        doc_id = self.document_ids[index]
        
        return doc_method(doc_id)     
        
    def save(self):
        """
        Saves the class instance to disk.
        """
        save_path = _get_save_base_path(self._user_api, create_folder_if_no_exist = True)
        
        #TODO: What should the file name be ...

        with open(save_path, "wb") as f:
            pickle.dump(self,f)
        return None

    def get_changes_from_old_version(self,old_self):
        return analysis.LibraryIDDifferences(self,old_self)
    
    #NOTE: I'm not sure if I want to pass in an old version for comparison
    #or if I want to have the old version get the new version
    #def get_updates(self,old_obj):
    #    return LibraryIDDifferences(self,old_obj)
         

            
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
    