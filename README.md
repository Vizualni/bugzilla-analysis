## Bugzilla-analysis

This is project I made for class called *seminar*.

Main point of this is to analize data on bugzilla pages and create ranking
list of best software.

ToDo List:
* Add support for questom queries
* Transfer all data to MySQL database
* Automatic downloading and farming bugs for later analysis

Example of usage.
```python
from core.base import FedoraBugzilla
from core.base import BugzillaAnalysis
fedoraBugzilla = FedoraBugzilla()
result = fedoraBugzilla.getBugs("curl")
bugZilla = BugzillaAnalysis()
bugZilla.load(result)
bugZilla.start() #creates image and saves is on hard drive (for now)
```
