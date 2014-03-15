import urllib
import urllib2

class downloader(object):
	url = None

	"""Downloading data from web"""
	def __init__(self, url=None):
		self.setURL(url)

	"""TODO MUST ADD ERROR CHECKING"""
	def setURL(self, url):
		self.url = url

	"""Returns downloaded data from self.url"""
	def download(self):
		data = None
		try:
			request = urllib2.urlopen(self.url)
			data = request.read()
		except:
			print "Error. Handle this! (LATER)"

		return data