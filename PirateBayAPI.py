#!/usr/bin/env python
# encoding: utf-8
"""

PirateBayAPI.py
Written By PirosB3, http://pirosb3.com

"""

from google.appengine.api import urlfetch
from urllib import quote

# TODO: Make order for, for now order by seed

class PirateBayAPI():
    """This component is used to generate results for thepiratebay.org"""
    uri = 'http://thepiratebay.org'
    
    def requestResultsForValue(self, value):
        """return an array of results given a value as input"""
        if (value == ''): raise "Please insert a valid value"
        
        # Generate URI and make call to ThePirateBay
        call = "%s/search/%s/0/7/0" % (self.uri, quote(value))
        result = urlfetch.fetch(call)
        
        # TODO: Parse URL
        return result
        