from core.downloader import downloader
import core.fedora_bugzilla as fedora
"""
Naravno nece biti ovako 'smotano', nego sada cisto za prvu ruku
da vidite dali je to dobro. Ako budete pokretali, morate znati
da je njihova stranica uzasno spora jer treba svih 1000 redaka
ispisati.
"""
def main():
	test_url = "https://bugzilla.redhat.com/buglist.cgi?bug_status=__open__&"\
		"content=linux&no_redirect=1&order=relevance%20desc&product=&query_format=specific"

	d = fedora.fedora_bugzilla(test_url)
	print "Running..."
	data = d.run()
	for dd in data:
		print dd

if __name__ == '__main__':
	main()