import re
from downloader import downloader as downloader
"""(Interface) Extracts all data from webpage"""
class extractor(object):

	def __init__(self, url):
		pass

	"""Returns all data from website in form of entity array."""
	def run(self):
		return self.getData();

	def getData(self):
		raise NotImplementedError("Should implement!")
