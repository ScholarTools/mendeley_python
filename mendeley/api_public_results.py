# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 09:08:55 2014

@author: jameshokanson
"""

class PublicJournalArticle(object):
    
    """
    THIS IS A WORK IN PROGRESS
    """
    def __init__(self,json_data):
        #super(self.__class__,self).__init__(json_data)

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
     
     
class PublicDocumentEntry(object):
    
    @staticmethod
    def createObject(json_data):
        doc_type = json_data['type']
        if doc_type is 'Journal Article':
            return PublicJournalArticle(json_data)
        else:
            raise Exception('Unhandled document type: %s' % doc_type)

class TopAuthor(object):
    
    """
    See more information on this object at:
    @DOC: http://apidocs.mendeley.com/home/public-resources/stats-authors
    
    I've posted some questions there which may or may not ever get answered :/
    
    See Also:
    .api.PublicMethods.get_top_authors
    """
    
    #TODO: Build rank into class, in case things are shuffled ...
    def __init__(self,json):
        self.name  = json['name']
        self.value = json['value']
        #?? - do we want to know the discipline as well????
        #This would require passing this in based on the request