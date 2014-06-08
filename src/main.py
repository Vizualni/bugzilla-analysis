#!/usr/bin/python
from core.base import FedoraBugzilla
from core.base import BugzillaAnalysis

fedoraBugzilla = FedoraBugzilla()
result = fedoraBugzilla.getBugs("curl")
bugZilla = BugzillaAnalysis()
bugZilla.load(result)
bugZilla.start()