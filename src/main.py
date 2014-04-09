#!/usr/bin/python
from core.base import FedoraBugzilla
from core.base import xmlFedoraBugzilla

fbzla = FedoraBugzilla()
running = False

def main():
	run()
	d = xmlFedoraBugzilla()
	print "Running..."
	print d.getBugs("curl")
	print d.getBugs("webcam")

def run():
	while running:
		printMenu()
		getUserInputAndDoIt()

def printMenu():
	print "Welcome to the SuperAwesomeBugzillaAnalysis software!"
	print "Choose one of the options: "
	print " 1) Search for new bugs!"
	print " 2) Do the autosearch! <- this (should) be awesome"
	print " 3) Analyze!"
	print " q) Exit!"

def exit():
	global running
	running = False

def getUserInputAndDoIt():
	inp = raw_input().lower()
	if inp=="q":
		print "Exiting...:("
		exit()


if __name__ == '__main__':
	main()