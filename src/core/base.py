#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import os
import re
import sys
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import xml.etree.ElementTree as ET
from pyzilla import BugZilla as xmlrpcBugzilla_import
DEBUG = True

def debug(msg):
    if DEBUG:
        print msg

def isInteger(string):
    try:
        int(string)
        return True
    except:
        return False

class DatabaseInterface():
    """
    This is interface that every database should implement.

    """
    def getBugByBugId(self, bug_id):
        """ Gets bug by bug id. """
        raise NotImplementedError()

    def saveBugs(self, bug):
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

    def setProductName(self, pn):
        self.__productName = str(pn)


class XMLDatabase(DatabaseInterface):
    __folder = "./data/"
    __filename_template = "bugzilla-database-%s.xml"
    __filename_regex = "bugzilla-database-([a-zA-Z0-9 \.]+)\.xml"
    __productName = ""

    def __getAllFiles(self):
        """Gets all files that match bugzilla format."""
        files = []
        for f in os.listdir(this.__folder):
            if f.endswith(".xml"):
                rm = re.match(self.__filename_regex, f)
                if rm is not None:
                    files.append(f)
        return files

    def __getCurrentFile(self):
        """Returns current file to write xml file in."""
        filename = self.__folder + self.__filename_template %(self.__productName)
        if not os.path.isfile(filename):
            tmp = ET.Element("bugs")
            ttree = ET.ElementTree(tmp)
            ttree.write(filename)
        return filename

    def __createNewXMLFile(self):
        """Creates empty XML file and return its filename."""
        if len(self.__productName)==0:
            raise ValueError("You must set product name")
        for f in self.__getAllFiles():
            rm = re.match(self.__filename_regex, f)
            if rm is not None:
                indexSet.add(rm.group(0))
        filename = self.__filename_template % (self.__productName)
        root = ET.Element("bugs")
        tree = ET.ElementTree(root)
        tree.write(filename)
        return filename

    def __getListOfBugsFromXML(self, xml):
        """Gets list of bugs from xml file that has been downloaded."""
        list_of_bugs = []
        fields = FedoraBugzillaEntity().getFields()
        for child in xml:
            if child.tag!="bug":
                continue
            newBug = ET.Element("bug")
            for child_tag in child:
                if child_tag.tag in fields:
                    newField = ET.SubElement(newBug, child_tag.tag)
                    newField.text = child_tag.text
            list_of_bugs.append(newBug)
        return list_of_bugs

    def saveBugs(self, bugs):
        """ Saves bugs in database on disk. """
        list_of_bugs = []
        if isinstance(bugs, basestring):
            try:
                tree_bugs = ET.fromstring(bugs)
                list_of_bugs = self.__getListOfBugsFromXML(tree_bugs)
            except Exception, e:
                print "Error while trying to save bugs."
                print e
                return None
        elif isinstance(bugs, ET.ElementTree):
            list_of_bugs = self.__getListOfBugsFromXML(bugs)
        elif type(bugs) is dict:
            for bug in bugs["bugs"]:
                novi_bug = FedoraBugzillaEntity()
                novi_bug.saveFromDict(bug)
                #novi_bug.printMe()
                list_of_bugs.append(novi_bug.getAsXML())
        debug( "There are %d bugs for %s"%(len(list_of_bugs), self.__productName) )
        current_file = self.__getCurrentFile()
        tree = ET.parse(current_file)
        root = tree.getroot()
        for bug in list_of_bugs:
            root.append(bug)
        try:
            tree.write(current_file)
        except Exception, e:
            print "Error while saving to database: ", e
            return None
        return list_of_bugs

    def createEntity(self, data):
        raise NotImplementedError("")

class Downloader(object):
    """ NO LONGER IN USE"""
    __url = None
    __postData = None
    __chunkSize = 8192/2
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
        data = ""
        try:
            request = None
            if self.__postData == None:
                request = urllib2.urlopen(self.__url)
            else:
                request = urllib2.urlopen(self.__url, self.__postData)
            size = 0
            try:
                size = int(request.info().getheaders("Content-Length")[0].strip())
            except:
                pass
            bytes_read = 0
            while 1:
                tmp_data = request.read(self.__chunkSize)
                bytes_read = len(data)
                sys.stdout.write("--- Downloaded %.3fmb out of %.3fmb\r" %( bytes_read/(1024.0*1024.0), size/(1024.0*1024)))
                if not tmp_data:
                    sys.stdout.write("\n")
                    break
                data += tmp_data
        except Exception, e:
            print "No internet connection...I guess. ----> "
            print "=ERROR= ",e
        return data

    def downloadPostRequest(self, post_data=[]):
        if type(post_data) is not list:
            raise ValueError("Post data must be list of tuples where first item in tuple is key, second is value.")
        data = None
        try:
            self.__postData = urllib.urlencode(post_data)
            data = self.download()
        finally:
            self.__postData = None
        return data

class BugzillaException(Exception):
    """Error raise for enything related to bugzilla."""
    pass

class BugzillaBaseClass(object):
    """Base class for all bugzilla classes."""

    def __init__(self):
        self.downloader = Downloader()
        self.db = XMLDatabase()

    def setSearchWord(self, sw):
        """Sets word to search for in online bug database."""
        self.__search_word = str(sw)

    def getSearchWord(self):
        return self.__search_word

    def getBugs(self, search_word):
        self.db.setProductName(search_word)
        if search_word is not None:
            self.setSearchWord(search_word)
        debug("Starting download...")
        all_bugs = self.xmlrpc.Bug.search({"component":str(self.getSearchWord())})
        debug("Download complete.")
        parsed_bugs = self.db.saveBugs(all_bugs)
        debug("Bugs saved.")
        return parsed_bugs

class FedoraBugzilla(BugzillaBaseClass):
    url = "https://bugzilla.redhat.com/xmlrpc.cgi"
    def __init__(self):
        BugzillaBaseClass.__init__(self)
        self.xmlrpc = xmlrpcBugzilla_import(self.url, verbose = False)

class FedoraBugzillaNOXML(BugzillaBaseClass):
    """Old but gold :(. Not in use anymore."""
    __base_url = "https://bugzilla.redhat.com"
    __test_url_template = __base_url + "/buglist.cgi?query_format=specific&order=relevance+desc&bug_status=__open__"\
    "&product=&content=%s"
    #maknut OPEN. Tako ih ima vise.
    __search_word = "linux"
    __url_for_all_bugs = __base_url + "/show_bug.cgi"
    def __init__(self, search_word = "linux"):
        super(FedoraBugzilla, self).__init__()

    def getBugs(self, search_word=None):
        """ Finds all bugs for given search word. Also sets search word. """
        if search_word is not None:
            self.setSearchWord(search_word)
        url = self.__test_url_template % (urllib.quote(self.__search_word))
        print "Searching for:", self.__search_word
        self.downloader.setURL(url)
        data = self.getListOfBugIds()
        print "Got info about %d bugs. Now downloading them." % (len(data))
        post_data = [("ctype", "xml"), ("excludefield", "attachmentdata")]
        for bug_id in data:
            post_data.append( ("id", str(bug_id)) )
        print "Downloading! This could take a while. PATIENCE YOU MUST HAVE my young padawan."
        self.downloader.setURL(self.__url_for_all_bugs)
        xml_of_all_bugs = self.downloader.downloadPostRequest(post_data)
        print "Downloaded!"
        print "Saving..."
        try:
            self.db.saveBugs(xml_of_all_bugs)
        except Exception, e:
            print "=ERROR= ",
            print e.message
            return False
        return True

    def getListOfBugIds(self):
        """Returns list of bug ids for search word from html.
            Bug id is a number and first element one in table row!
        """
        data = self.downloader.download()
        print "Downloaded! Now extracting data and looking for bug id's."
        result = []
        #regex_for_single_item = r"<tr id=\"b\d+\" class=\"bz_bugitem.+?<\/tr>"
        regex_for_single_item = r"<tr[^>]*>.+?<\/tr>"
        regex_for_td = r"<td[^>]*>(.+?)<\/td>"
        regex_to_remove_tags = r"<[^>]*>"
        result1 = re.findall(regex_for_single_item, data, re.M | re.DOTALL)
        #I must find each td and get only what's inside of it (without a tag)
        for res in result1:
            one_entity = []
            without_td = re.findall(regex_for_td, res, re.M | re.DOTALL)
            for x in xrange(len(without_td)):
                one_entity.append(re.sub(regex_to_remove_tags, '', without_td[x]).strip())
            try:
                bug_id = one_entity[0]
                if isInteger(bug_id):
                    result.append(bug_id)
            except:
                pass #do nothing
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
    def getAttr(self, name):
        if name in self.fields:
            return self.fields[name]

    def setAttr(self, name, value):
        #print "TRAZIM PRISTUP ZA ", name, value
        if name in self.fields:
            self.fields[name] = value
        elif "bug_"+name in self.fields:
            self.fields["bug_"+name] = value
        else:
            self.fields[name]=value

    def saveFromDict(self, dict_to_parse):
        for field in dict_to_parse:
            self.setAttr(field, dict_to_parse[field])

    def getAsXML(self):
        newBug = ET.Element("bug")
        for key in self.fields:
            if self.fields[key] is not None:
                try:
                    newField = ET.SubElement(newBug, key)
                    newField.text = str(self.fields[key])
                except:
                    pass
                    #print "error kod str unicode:("
        return newBug

    def getFields(self):
        return self.fields

    @staticmethod
    def getEntitiesFromListOfXML(list_of_xml):
        lista = []
        for xmlic in list_of_xml:
            tmp = {}
            for child in xmlic:
                tmp[child.tag] = child.text
            lista.append(tmp)
        return lista

class FedoraBugzillaEntity(Entity):
    fields = None

    def printMe(self):
        for k in self.fields:
            print k, "=>", self.fields[k]
        print ''

    def __init__(self):
        self.fields = {"bug_id": None,
            "creation_ts": None,
            "short_desc": None,
            "delta_ts": None,
            "reporter_accessible": None,
            "cclist_accessible": None,
            "classification_id": None,
            "classification": None,
            "product": None,
            "component": None,
            "version": None,
            "rep_platform": None,
            "op_sys": None,
            "bug_status": None,
            "priority": None,
            "bug_severity": None,
            "target_milestone": None,
            "blocked": None,
            "everconfirmed": None,
            "reporter": None,
            "assigned_to": None,
            "qa_contact": None,
            "cf_doc_type": None,
            "cf_story_points": None,
            "cf_clone_of": None,
            "cf_type": None,
            "cf_regression_status": None,
            "cf_mount_type": None,
            "cf_documentation_action": None,
            "cf_category": None,
            "target_release": None}


class BugzillaAnalysis:
    """Where you can draw graphs and make some analysis."""

    def __loadByFilename(self, filename):
        raise NotImplementedError("Wait for it.")

    def __loadByXML(self, xml):
        raise NotImplementedError("Wait for it.")

    def __loadByListOfDicts(self, ld):
        raise NotImplementedError("Wait for it.")

    def __loadByListOfXMLBugs(self, list_xml):
        raise NotImplementedError("Wait for it.")

    def load(self, what):
        # !!!!! TREBA SKUZIT KOJEG JE TIPA, SADA TO AUTOMATSKI
        # RADIM I PRETPOSTAVLJAM DA JE LISTA XML-OVA
        self.__listOfDicts = Entity.getEntitiesFromListOfXML(what)

    def start(self):
        debug("Analysis started.")
        self.getByVersionCount()
        debug("Analysis complete.")

    def getByVersionCount(self, message=""):
        """saves image graph displaying bug count by version"""
        tmp = {}  # grupiranje po datumu
        for helpme in self.__listOfDicts:
            x = helpme["version"]
            if x.find("rawhide")!=-1:
                continue
            if x in tmp:
                tmp[x]+=1
            else:
                tmp[x]=1
        data, values = tmp.keys(), tmp.values()
        plt.bar(range(len(data)), values, align='center')
        plt.xticks(range(len(data)), data, rotation=90, size='small')
        plt.xlim([0, len(data)])
        plt.ylim([0, max(values)+1])
        plt.savefig('image.png')
        plt.show()
