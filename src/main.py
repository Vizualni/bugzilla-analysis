#!/usr/bin/python
from core.base import FedoraBugzilla
from core.helpers import run

def main():
	run()
	d = FedoraBugzilla()
	print "Running..."
	print d.getBugs("webcam")
	print d.getBugs("curl")
if __name__ == '__main__':
	main()