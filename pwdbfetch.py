#!/usr/bin/python
import sys
import urllib2

def downloadImage(prefix, itemId):
	url = 'http://www.pwdatabase.com/images/icons/general%s/%d.gif' % (prefix, itemId)
	filename = '%s/%d.gif' % (prefix, itemId)
	try:
		response = urllib2.urlopen(url)
		data = response.read()
		output = open(filename, 'wb')
		output.write(data)
		output.close()
		print 'downloaded %s' % (filename)
	except:
		print 'received 404 on %s/%d' % (prefix, itemId)
	

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print 'Usage: pwdbfetch.py <startID> <endID>'
		sys.exit(0)
		
	startId = int(sys.argv[1])
	endId = int(sys.argv[2])
	
	for itemId in range(startId, endId+1):
		downloadImage('m', itemId)
		downloadImage('f', itemId)