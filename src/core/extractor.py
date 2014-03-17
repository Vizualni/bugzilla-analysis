#!/usr/bin/python
import re


class Extractor(object):
	"""(Interface) Extracts all data from webpage"""

	def __init__(self, url):
		pass

	def run(self):
		"""Returns all data from website in form of entity array."""
		return self.getData();

	def getData(self):
		raise NotImplementedError("Should implement!")
