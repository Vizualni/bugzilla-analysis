#!/usr/bin/python
from core.downloader import Downloader
from core.fedora_bugzilla import FedoraBugzilla

def main():
	test_url = "https://bugzilla.redhat.com/buglist.cgi?bug_status=__open__&"\
		"content=linux&no_redirect=1&order=relevance%20desc&product=&query_format=specific"
	print "Url: ", test_url
	d = FedoraBugzilla(test_url)
	print "Running..."
	data = d.run()
	for dd in data:
		print dd

if __name__ == '__main__':
	main()