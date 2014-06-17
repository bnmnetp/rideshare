import urllib

def geocode(address):
 # This function queries the Google Maps API geocoder with an
 # address. It gets back a csv file, which it then parses and
 # returns a string with the longitude and latitude of the address.

 # This isn't an actual maps key, you'll have to get one yourself.
 # Sign up for one here: http://code.google.com/apis/maps/signup.html
  mapsKey = 'onk1an5ac8ABQIAAAAg9WbCE_zwMIRW7jDFE_3ixQlKBzOsZLiKVvY0J60oIHyvyt2BhQBmJex9U1i3T7I95SaF5Yg7fgabA'
  mapsUrl = 'http://maps.google.com/maps/geo?q='
     
 # This joins the parts of the URL together into one string.
  url = ''.join([mapsUrl,urllib.quote(address),'&output=csv&key=',mapsKey])
    
 # This retrieves the URL from Google, parses out the longitude and latitude,
 # and then returns them as a string.
  coordinates = urllib.urlopen(url).read().split(',')
  coorText = '%s,%s' % (coordinates[3],coordinates[2])
  return coorText



print geocode('plymouth, mn')
