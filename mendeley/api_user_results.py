# -*- coding: utf-8 -*-
"""
Insert description here
"""

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
    
    