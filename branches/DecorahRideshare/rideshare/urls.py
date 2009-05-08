from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/profile/$', 'findaride.views.menu'),  ## workaround login profile
    (r'^accounts/', include('registration.urls')),
    (r'^rideshare/', include('findaride.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/bmiller/Projects/RideShare/rideshare/static'}),

)


