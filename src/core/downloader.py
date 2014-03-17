#!/usr/bin/python
import urllib
import urllib2

class Downloader(object):
	
	url = None

	def __init__(self, url=None):
		"""Downloading data from web"""
		self.setURL(url)

	def setURL(self, url):
		"""TODO MUST ADD ERROR CHECKING"""
		self.url = url

	def download(self):
		"""Returns downloaded data from self.url"""
		data = None
		try:
			request = urllib2.urlopen(self.url)
			data = request.read()
		except:
			print "Error. Handle this! (LATER)"

		return data