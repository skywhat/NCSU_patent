import urllib
import urllib2

url="http://licensing.research.ncsu.edu/technologies"

values1={"limit":200,"offset":0}
values2={"limit":200,"offset":200}
data1=urllib.urlencode(values1)
data2=urllib.urlencode(values2)

theurl1=url+"?"+data1
theurl2=url+"?"+data2

r1=urllib2.urlopen(theurl1)
r2=urllib2.urlopen(theurl2)

f1=open("1.html","w")
f1.write(r1.read())
f1.close()

f2=open("2.html","w")
f2.write(r2.read())
f2.close()


