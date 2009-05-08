from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField

class Category(models.Model):
    cat_name = models.CharField(blank=True, max_length=100)
    cat_code = models.CharField(blank=True, max_length=20)
    dest_label = models.CharField(blank=True, max_length=50)    
    hover_message = models.CharField(blank=True, max_length=100)    
    def __unicode__(self):
        """docstring for __unicode__"""
        return self.cat_name

class City(models.Model):
    city_name = models.CharField(blank=False,null=False, max_length=100)
    state = USStateField(blank=False)
    zip_code = models.IntegerField(blank=True, null=True)    

    def __unicode__(self):
        return self.city_name + u" " + self.state

class RiderProfile(models.Model):
    userId = models.ForeignKey(User, unique=True)
    car = models.CharField(max_length=30)
    home = models.ForeignKey(City)
    phone_number = PhoneNumberField(blank=True)


class Destination(models.Model):
    destination_name = models.CharField(blank=True, max_length=100)
    city = models.ForeignKey(City)
    cat = models.ForeignKey(Category)
    

    def __unicode__(self):
        return self.destination_name + u" in " + self.city.__unicode__()

class Trip(models.Model):
    num_passengers = models.IntegerField(blank=True, null=True, default=0)
    max_passengers = models.IntegerField(blank=True, null=True, default=1)
    destination = models.ForeignKey(Destination)
    driver = models.ForeignKey(User,null=True,blank=True)
    riders = models.ManyToManyField(User,blank=True,related_name="ride") #,filter_interface=models.VERTICAL
    start_point = models.ForeignKey(City)
    date_of_trip = models.DateField(blank=True,null=True)
    date_added = models.DateTimeField(blank=True, auto_now_add=True)
    requests = models.ManyToManyField(User,blank=True,related_name="ride_request") #,filter_interface=models.VERTICAL)
    comment = models.TextField(blank=True, null=True)
    
#    class Meta:
#        unique_together = ['destination','driver','start_point','date_of_trip','cat']
#    exercises bug: 6523  in django and postgresql
#

    def __unicode__(self):
        return self.destination.destination_name + u", " + \
               self.destination.city.__unicode__() + u" on " + \
               unicode(self.date_of_trip)


class Hints(models.Model):
    date_added = models.DateTimeField(blank=True, auto_now_add=True)
    text = models.TextField(blank=False, null=False)


    