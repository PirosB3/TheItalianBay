#!/usr/bin/env python
# encoding: utf-8
"""

PirateBayAPI.py
Written By PirosB3, http://pirosb3.com

"""

from google.appengine.api import urlfetch
from google.appengine.api import memcache

from urllib import quote
import re

from BeautifulSoup import BeautifulSoup

import logging
import os


"""This component is used to generate results for thepiratebay.org"""
TWO_HOURS = 7200
URI = 'http://thepiratebay.se'
SIZE_RE = re.compile('Size\s+(\d+(?:\.\d+)?\s+[A-Za-z]+)')
MAGNET_RE = re.compile('^magnet:')

ORDER_BY = {
    'SE'   : 7,
    'LE'   : 9,
    'name' : 1,
    'type' : 13,
    'size' : 5
}

FILTER_BY = {
    'audio'        : 100,
    'video'        : 200,
    'audio'        : 100,
    'applications' : 300,
    'games'        : 400,
    'other'        : 600,
    'none'         : 0
}

urlfetch_fetch = urlfetch.fetch

def CacheControlled(function):
    """this function should be called by each API call, it's use is to return cached data or cache when possible"""
    def wrapper(*args, **kwargs):
        # If cache is disabled (testing) we will just call the API
        cache_disabled = kwargs.pop('disable_cache', False)
        if cache_disabled:
            return function(*args, **kwargs)

        # Generate a function unique ID
        unique_string = repr((args, kwargs))
        function__name__ = function.__name__

        # if cache warming, then avoid fetching from cache.
        cached_result = None
        cache_warming = kwargs.pop('cache_warming', False)
        if not cache_warming:
            cached_result = memcache.get(unique_string, function__name__)

        # check if in cache, if it is just return the result
        if cached_result:
            logging.debug("GOT CACHED: %s and %s" % (unique_string, function__name__)) 
            return cached_result

        # Let's run the function and cache it ;)
        result = function(*args, **kwargs)
        r = memcache.add(unique_string, result, TWO_HOURS, 0, function__name__)

        logging.debug("NEW CACHE: %s and %s" % (unique_string, function__name__))

        return result
    return wrapper

def __lookupConstant(lookup, key, fallback):
    try:
        return lookup[key]
    except KeyError:
        return fallback

def __parseResult(result):
    """Returns a list of results, each result has: name, link, SE, LE"""

    def __processSingleRow(tr):
        detLink = tr.find("a", { "class" : "detLink" })
        detDesc = tr.find("font", { "class" : "detDesc" })
        hrefTag= tr.find(href=MAGNET_RE)
        se, le = tr.findAll('td')[2:4]
        return {
            'title': detLink.text,
            'href': hrefTag['href'],
            'size': SIZE_RE.findall(detDesc.text.replace("&nbsp;", ' '))[0],
            'SE': se.text,
            'LE': le.text
        }

    parser = BeautifulSoup(result)

    # find results within table #searchResult and get a list of rows
    resultsTable = parser.find('table', {'id' : 'searchResult'})
    if not resultsTable:
        return []

    # Remove all the faulty rows
    resultsRows = filter(lambda tr: len(tr.findAll('td')) == 4, resultsTable.findAll("tr")[1:])

    # Iterate over each row and store results in list
    return map(__processSingleRow, resultsRows)

def __fetch(call):
    """returns content from URL"""
    result = urlfetch_fetch(call).content
    if not result:
        raise Exception("There was an error fetching the url: " + call)

    return result

@CacheControlled
def requestMagnetLinkForResultURL(url):
    """return a url leading to torrent giving a description url as input"""
    if (url == ''): raise Exception("Please insert a valid value")

    # Fetch description page
    page = __fetch(URI + url)

    parser = BeautifulSoup(page)
    torrent_url = parser.find('div', {'class' : 'download'}).findAll('a')[1]['href']

    return torrent_url


@CacheControlled
def requestResultsforTop100(filter_name="none"):
    """returns an array of the top 100 torrents of a category, defaults to all"""

    call ="%s/top/%s" % (URI, __lookupConstant(FILTER_BY, filter_name, 0))
    result = __fetch(call)

    return __parseResult(result)

@CacheControlled
def requestResultsforRecentUploads():
    # return an array of recently uploaded torrents
    call = "%s/recent" % URI
    result = __fetch(call)

    # Fetch results array and trim last value
    torrentArray= __parseResult(result)
    return torrentArray[:len(torrentArray)-1]

@CacheControlled
def requestResultsForValue(value, orderBy= 'SE', filter_name = 'none'):
    """return an array of results given a value as input, optional values are filter and orderBy"""

    # validate
    if (value == ''):
        raise Exception("Please insert a valid value")

    # Generate URI and make call to ThePirateBay
    call = "%s/search/%s/0/%s/%s" % (URI, quote(value),
            __lookupConstant(ORDER_BY, orderBy, 1),
            __lookupConstant(FILTER_BY, filter_name, 0))
    result = __fetch(call)

    return __parseResult(result)
