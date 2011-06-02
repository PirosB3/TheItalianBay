#!/usr/bin/env python
# encoding: utf-8
"""

PirateBayAPI.py
Written By PirosB3, http://pirosb3.com

"""

from google.appengine.api import urlfetch
from urllib import quote

from libs.BeautifulSoup import BeautifulSoup

# TODO: Make order for, for now order by seed

class PirateBayAPI():
    """This component is used to generate results for thepiratebay.org"""
    uri = 'http://thepiratebay.org'
    
    def __parseResult(self, result):
        """Returns a list of results, each result has: name, link, SE, LE"""
    	parser = BeautifulSoup(result)
        results = []
        
    	# find results within table #searchResult and get a list of rows
    	resultsTable = parser.find('table', {'id' : 'searchResult'})
    	if resultsTable == None: return {}
    	
    	resultRows = resultsTable.findAll("tr")
    	
        # Iterate over each row and store results in list
        if (len(resultRows) == 0 or resultRows == None): return {}
    	for result in resultRows:
    	    
            # Get all defenitions in row and initialize empty dictionary
    		elements = result.findAll('td')
    		current = {}
    		
            # Iterate!
    		for position, item in enumerate(elements):
    			if position == 1:
    				link = item.find("a", { "class" : "detLink" })
    				current['title'] = link.text
    				current['permalink'] = link['href']
    			if position == 2:
    				current['SE'] = item.text
    			if position == 3:
    				current['LE'] = item.text
    		results.append(current)
            # Validate iteration has been done correctly
        
        return results
    
    def requestResultsForValue(self, value):
        """return an array of results given a value as input"""
        if (value == ''): raise "Please insert a valid value"
        
        # Generate URI and make call to ThePirateBay
        call = "%s/search/%s/0/7/0" % (self.uri, quote(value))
        result = urlfetch.fetch(call).content
        
        # TODO: Parse URL
        return self.__parseResult(result)