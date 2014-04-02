#!/usr/bin/python
import urllib
import urllib2
import os
import re
import xml.etree.ElementTree as ET

class DatabaseInterface():
	"""
	This is interface that every database should implement.

	"""
	def getBugByBugId(self, bug_id):
		""" Gets bug by bug id. """
		raise NotImplementedError()

	def saveBug(self, bug):
		""" Saves bug (finds bug by bug.id and replaces it). """
		raise NotImplementedError()

	def insertBug(self, bug):
		""" Inserts new bug into database. """
		raise NotImplementedError()

	def deleteBugByBugId(self, bug_id):
		""" Deletes bug whose id is bug_id. """
		raise NotImplementedError()

	def removeDuplicates(self, bug_id):
		""" Removes duplicates from database.
		If found keeps one that is newer. """
		raise NotImplementedError()

	def getEntity(self, bug):
		""" Gets globally represented entity from xml """
		raise NotImplementedError()


class XMLDatabase(DatabaseInterface):
	__folder = "./data/"
	__filename_template = "bugzilla-database-%d.xml"
	__filename_regex = "bugzilla-database-(\d+)\.xml"
	__current_file_index = 1
	def __getAllFiles(self):
		files = []
		for f in os.listdir(this.__folder):
			if f.endswith(".xml"):
				rm = re.match(self.__filename_regex, f)
				if rm is not None:
					files.append(f)
		return files

	def __getCurrentFile(self):
		"""Returns current file to write xml file in."""
		filename = self.__folder + self.__filename_template %(self.__current_file_index)
		if not os.path.isfile(filename):
			tmp = ET.Element("bugs")
			ttree = ET.ElementTree(tmp)
			ttree.write(filename)
		return filename

	def __createNewXMLFile(self):
		"""Creates empty XML file and return its filename."""
		i = 1 # current database index.
		indexSet = set()
		for f in self.__getAllFiles():
			rm = re.match(self.__filename_regex, f)
			if rm is not None:
				indexSet.add(rm.group(0))
		while True:
			if i not in indexSet:
				break
			i+=1
		self.__current_file_index = i
		filename = self.__filename_template % (__current_file_index)
		root = ET.Element("bugs")
		tree = ET.ElementTree(root)
		tree.write(filename)
		return filename

	def saveBugs(self, bugs):
		""" Saves bugs in database on disk. """
		"""if bugs is string:
		elif bugs is list:
		el"""
		current_file = self.__getCurrentFile()
		tree = ET.parse(current_file)
		root = tree.getroot()
		for bug in bugs:
			root.append(bug)
		tree.write(current_file)

	def createEntity(self, data):
		raise NotImplementedError("DOVRSI OVO")

class Downloader(object):
	__url = None
	__postData = None
	def __init__(self, url=None):
		"""Downloading data from web"""
		self.setURL(url)

	def setURL(self, url):
		"""TODO MUST ADD ERROR CHECKING"""
		self.__url = url

	def getUrl(self):
		return self.__url

	def download(self):
		"""Returns downloaded data from self.url"""
		if self.__url is None:
			raise ValueError("You must set url.")
		data = None
		try:
			request = None
			if self.__postData is None:
				request = urllib2.urlopen(self.__url)
			else:
				request = urllib2.urlopen(self.__url, self.__postData)

			data = request.read()
		except:
			print "No internet connection...I guess."

		return data

	def downloadPostRequest(self, post_data=[]):
		if type(post_data) is not list:
			raise ValueError("Post data must be list of tuples where first item in tuple is key, second is value.")
		data = None
		try:
			self.__postData = urllib.urlencode([("id", 123), ("id", 333)])
			data = self.download()
		finally:
			self.__postData = None
		return data



class Extractor(object):
	"""(Interface) Extracts all data from webpage"""

	def __init__(self, url):
		pass

	def run(self):
		"""Returns all data from website in form of entity array."""
		return self.getData();

	def getData(self):
		raise NotImplementedError("Should implement!")


class BugzillaException(Exception):
	"""Error raise for enything related to bugzilla."""
	pass

class FedoraBugzilla(Extractor):

	__test_url_template = "https://bugzilla.redhat.com/buglist.cgi?bug_status=__open__&"\
		"content=%s&no_redirect=1&order=relevance%%20desc&product=&query_format=specific"
	__search_word = "linux"
	__url_for_all_bugs = "https://bugzilla.redhat.com/show_bug.cgi"
	def __init__(self, search_word = "linux"):
		#super(FedoraBugzilla, self).__init__(url)
		self.downloader = Downloader()
		self.db = XMLDatabase()

	def setSearchWord(self, sw):
		self.__search_word = str(sw)

	def getBugs(self, search_word=None):
		""" Finds all bugs for given search word. Also sets search word. """
		if search_word is not None:
			self.setSearchWord(search_word)
		url = self.__test_url_template % self.__search_word
		self.downloader.setURL(url)
		data = self.getData()
		print "Got info about %d bugs. Now downloading them." % (len(data))
		post_data = [("ctype", "xml"), ("excludefield", "attachmentdata")]
		
		for d in data:
			bug_id = d[0]
			post_data.append( ("id", str(bug_id)) )
		print "Downloading! This could take a while. PATIENCE YOU MUST HAVE my young padawan."
		xml_of_all_bugs = self.downloader.downloadPostRequest(post_data)
		print "Downloaded!"
		print "Saving..."


	def getData(self):
		"""Returns parsed data from url"""
		print "Downloading from: "+self.downloader.getUrl()
		data = self.downloader.download()
		print "Downloaded! Now extracting data."
		result = []
		regex_for_single_item = r"<tr id=\"b\d+\" class=\"bz_bugitem.+?<\/tr>"
		regex_for_td = r"<td[^>]*>(.+?)<\/td>"
		regex_to_remove_tags = r"<[^>]*>"

		result1 = re.findall(regex_for_single_item, data, re.M | re.DOTALL)

		#I must find each td and get only what's inside of it (without a tag)
		for res in result1:
			one_entity = []
			without_td = re.findall(regex_for_td, res, re.M | re.DOTALL)
			for x in xrange(len(without_td)):
				one_entity.append(re.sub(regex_to_remove_tags, '', without_td[x]).strip())
			result.append(one_entity)
		return result

	def getBugById(self, bug_id=None):
		""" Gets bug by id and returns it in XML format (ElementTree xml format)."""
		if bug_id==None:
			raise BugzillaException("bug_id can't be empty")
		self.downloader.setURL("https://bugzilla.redhat.com/show_bug.cgi?ctype=xml&id=%s"%(str(bug_id)))	
		data = self.downloader.download()
		xml = ET.fromstring(data)
		newBug = ET.Element("bug")
		fields = FedoraBugzillaEntity().getFields()
		for child in xml[0]:
			if child.tag in fields:
				newField = ET.SubElement(newBug, child.tag)
				newField.text = child.text
		return newBug



class Entity:
	"""This is one entity from database.
	It is going to access for data like this:
	entity1 = extractor(...).getData(...)[0]
	print entity1.ID, entity1.bugs, entity1.software_name
	while bugs is also going to be entity...
	ORM
	"""
	def __getattr__(self, name):
		if name in self.fields:
			return self.fields[name]
		raise AttributeError(name + " doesnt exists")

	def __getattr__(self, name, value):
		if name in self.fields:
			self.fields[name] = value
		raise AttributeError(name + " doesnt exists")

	def getFields(self):
		return self.fields

class FedoraBugzillaEntity(Entity):
	fields = None

	def __init__(self):
		self.fields = {"bug_id":None,
			"creation_ts":None,
			"short_desc":None,
			"delta_ts":None,
			"reporter_accessible":None,
			"cclist_accessible":None,
			"classification_id":None,
			"classification":None,
			"product":None,
			"component":None,
			"version":None,
			"rep_platform":None,
			"op_sys":None,
			"bug_status":None,
			"priority":None,
			"bug_severity":None,
			"target_milestone":None,
			"blocked":None,
			"everconfirmed":None,
			"reporter":None,
			"assigned_to":None,
			"qa_contact":None,
			"cf_doc_type":None,
			"cf_story_points":None,
			"cf_clone_of":None,
			"cf_type":None,
			"cf_regression_status":None,
			"cf_mount_type":None,
			"cf_documentation_action":None,
			"cf_category":None,
			"target_release":None}
