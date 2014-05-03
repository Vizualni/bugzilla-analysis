#!/usr/bin/python
from core.base import FedoraBugzilla
from core.base import BugzillaAnalysis
running = False

def main():
	run()
	d = FedoraBugzilla()
	print "Running..."
	res = d.getBugs("curl")
	ba = BugzillaAnalysis()
	ba.load(res)
	ba.start()

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