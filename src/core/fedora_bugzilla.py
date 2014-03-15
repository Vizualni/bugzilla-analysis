import extractor
import re
from downloader import *
class fedora_bugzilla(extractor.extractor):

	def __init__(self, url):
		super(fedora_bugzilla, self).__init__(url)
		self.down = downloader(url)
		pass

	def getData(self):
		print "Downloading..."
		data = self.down.download()
		print "Downloaded! Now extracting data."
		result = []
		regex_for_single_line = r"<tr id=\"b\d+\" class=\"bz_bugitem.+?<\/tr>"
		regex_for_td = r"<td[^>]*>(.+?)<\/td>"
		regex_to_remove_tags = r"<[^>]*>"
		result1 = re.findall(regex_for_single_line, data, re.M | re.DOTALL)

		#I must find each td and get only what's inside of it (without a tag)
		for res in result1:
			one_entity = []
			without_td = re.findall(regex_for_td, res, re.M | re.DOTALL)
			for x in xrange(len(without_td)):
				one_entity.append(re.sub(regex_to_remove_tags, '', without_td[x]).strip())
			result.append(one_entity)
		return result




