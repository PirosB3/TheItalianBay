#!/usr/bin/env python
# encoding: utf-8
"""

PirateBayAPI.py
Written By PirosB3, http://pirosb3.com

"""

from google.appengine.api import urlfetch
from urllib import quote
from re import findall

from BeautifulSoup import BeautifulSoup


"""This component is used to generate results for thepiratebay.org"""
uri = 'http://thepiratebay.org'

orderBy= [{'string' : 'SE', 'value' : 7}, {'string' : 'LE' , 'value' : 9}, {'string' : 'name' , 'value' : 1}, {'string' : 'type' , 'value' : 13}, {'string' : 'size' , 'value' : 5}]
filterBy = [{'string' : 'audio', 'value' : 100}, {'string' : 'video', 'value' : 200}, {'string' : 'audio', 'value' : 100}, {'string' : 'applications', 'value' : 300}, {'string' : 'games', 'value' : 400}, {'string' : 'other', 'value' : 600}, {'string' : 'none', 'value' : 0}]

def __getOrderByValue(value):
	# Returns a value used from TPB to identify order by, defaults to name
	for f in orderBy:
		if value == f['string']:
			return f['value']
	return 1
	
def __getFilterByValue(value):
	# Returns a value used from TPB to identify filter by, defaults to none
	for f in filterBy:
		if value == f['string']:
			return f['value']
	return 0

def __parseResult(result):
	"""Returns a list of results, each result has: name, link, SE, LE"""
	parser = BeautifulSoup(result)
	regex = 'Size\s+(\d+(?:\.\d+)?\s+[A-Za-z]+)'
	results = []
	
	# find results within table #searchResult and get a list of rows
	resultsTable = parser.find('table', {'id' : 'searchResult'})
	if resultsTable == None: return []
	
	# Iterate over each row and store results in list
	resultRows = resultsTable.findAll("tr")
	if (len(resultRows) == 0 or resultRows == None): return {}
	for result in resultRows:
		
		# Get all defenitions in row and initialize empty dictionary
		elements = result.findAll('td')
		current = {}
		
		# Iterate! ADD SIZE!!!!!!
		for position, item in enumerate(elements):
			if position == 1:
				link = item.find("a", { "class" : "detLink" })
				current['title'] = link.text
				current['permalink'] = link['href']
				
				# Use regex to get size
				string = item.find("font", { "class" : "detDesc" }).text
				current['size'] = findall(regex, string.replace("&nbsp;", ' '))[0]
			if position == 2:
				current['SE'] = item.text
			if position == 3:
				current['LE'] = item.text
		results.append(current)
		# Validate iteration has been done correctly
	
	# Remove item at index 0
	del results[0]
	return results

def __fetch(call):
	"""returns content from URL"""
	result = urlfetch.fetch(call).content
	if (result == None): raise Exception("There was an error fetching the url: " + call)
	
	return result

def __parseDescriptionPage(page):
	"""returns a dictionary with details from the page"""
	parser = BeautifulSoup(page)
	results = {}
	
	# Get torrent url
	url = parser.find('div', {'class' : 'download'}).find('a')['href']
	results['torrent_url'] = url
	
	# return data
	return results
	
def requestTorrentForResultURL(url):
	"""return a url leading to torrent giving a description url as input"""
	if (url == ''): raise Exception("Please insert a valid value")
	
	# Fetch description page
	page = __fetch(uri + url)
	
	# Parse result
	torrent_url = __parseDescriptionPage(page)['torrent_url']
	return __fetch(torrent_url)


def requestResultsforTop100(filter="none"):
	"""returns an array of the top 100 torrents of a category, defaults to all"""
	
	call ="%s/top/%s" % (uri, __getFilterByValue(filter))
	result = __fetch(call)
	
	return __parseResult(result)

def requestResultsforRecentUploads():
	# return an array of recently uploaded torrents
	call = "%s/recent" % uri
	result = __fetch(call)
	
    # Fetch results array and trim last value
	torrentArray= __parseResult(result)
	del torrentArray[-1]
	
	return torrentArray

def requestResultsForValue(value, orderBy= 'SE', filter = 'none'):
	"""return an array of results given a value as input, optional values are filter and orderBy"""
	
	# validate
	if (value == ''): raise Exception("Please insert a valid value")
	
	# Generate URI and make call to ThePirateBay
	call = "%s/search/%s/0/%s/%s" % (uri, quote(value), __getOrderByValue(orderBy), __getFilterByValue(filter))
	result = __fetch(call)
	
	return __parseResult(result)