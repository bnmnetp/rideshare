from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'findaride.views.menu'),
    (r'^newtrip/(\w+)', 'findaride.views.add_trip'),  
    (r'^help/$', 'findaride.views.help'),  
    (r'^contact/$', 'findaride.views.contact'),      
    (r'^add_trip/success/', 'findaride.views.thanks'),
    (r'^add_trip/notify/', 'findaride.views.driver_needed'),
    (r'^process_new_trip/$', 'findaride.views.process_new_trip'),    
    (r'^finalize_exact_match/(\d+)/$', 'findaride.views.finalize_exact_match'),
    (r'^add_trip/driver_notify/$', 'findaride.views.waitfordriver'),
    (r'^add_trip/newdriver/(\d+)/$', 'findaride.views.showriders'),    
    (r'^accept/(\d+)/(\d+)/$', 'findaride.views.add_rider'),    
    (r'^decline/(\d+)/(\d+)/$', 'findaride.views.decline_rider'),
    (r'^get_my_trips/$', 'findaride.views.get_my_trips'),
    (r'^edit_trip/(\d+)/$', 'findaride.views.edit_trip'),    
    (r'^edit_success/$', 'findaride.views.edit_success'),
    (r'^trip_deleted/$', 'findaride.views.trip_deleted'),
    (r'^driver_removed/$', 'findaride.views.driver_removed'),
    (r'^trip_updated/$', 'findaride.views.trip_updated'),
    (r'^quicksearch/$', 'findaride.views.quicksearch'),
    (r'^report_all_trips/$', 'findaride.views.alltrips'),
    (r'^report_all_users/$', 'findaride.views.allusers'),    
    url(r'^(\w+)/destination_ac/$', 'findaride.views.destination_ac', name='destination_ac'),
    url(r'^(\w+)/city_ac/$', 'findaride.views.city_ac', name='city_ac'),    
      
)