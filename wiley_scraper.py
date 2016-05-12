#!/usr/bin/python

import requests



baseURL = 'http://onlinelibrary.wiley.com/doi/'

'''
Old papers have ridiculously long DOIs. They include < > brackets in the middle, but sometimes they are not rendered
correctly in the DOI. In these cases, there will be '&lt;' instead of the 'less than' sign, and '&gt;' instead of the
'greater than' sign. Need to go through and check to make sure this didn't happen, or replace these strings if so.
'''

suffix = '/references/'

doi = input('DOI: ')

fullURL = baseURL + str(doi) + suffix

r = requests.get(fullURL)