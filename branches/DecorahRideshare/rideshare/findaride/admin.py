from django.contrib import admin
from findaride.models import *


class DestinationAdmin(admin.ModelAdmin):
    search_fields = ('destination_name','city')
 
class TripAdmin(admin.ModelAdmin):
    list_display = ('destination','max_passengers','num_passengers','driver', 'start_point', 'date_of_trip')

admin.site.register(Trip, TripAdmin)
admin.site.register(Destination, DestinationAdmin)
admin.site.register(City)
admin.site.register(Category)
admin.site.register(RiderProfile)
admin.site.register(Hints)