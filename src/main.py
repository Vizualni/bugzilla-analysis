#!/usr/bin/python
from core.base import FedoraBugzilla
import xmlrpclib

def main():
	
	d = FedoraBugzilla()
	print "Running..."
	print d.getBugs("wget")
if __name__ == '__main__':
	main()