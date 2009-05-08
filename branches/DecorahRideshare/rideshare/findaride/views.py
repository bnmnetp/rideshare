# Create your views here.
from datetime import datetime
from django import forms
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import USStateSelect, USPhoneNumberField, USStateField
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from findaride.models import Destination, Trip, City, Category, Hints
from jsonresponse import JsonResponse
from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from widgets import AutoCompleteWidget

import feedparser
import django.db.models
import random

# TODO clean up user friendliness of current implementation
# TODO: Add quicksearch


# TODO Send email to driver on the day of the trip to remind them about riders
# http://www.ecosherpa.com/category/news/feed/

def left_bar_data(request,trip_cat):
    """docstring for left_bar_data"""

    cat=get_category(trip_cat)
    trip_dict = {}
    # TODO Cache these selects, or cache this template?
    subq = 'SELECT COUNT(*) FROM findaride_trip_requests WHERE findaride_trip.id = findaride_trip_requests.trip_id'
    nt = Trip.objects.exclude(date_of_trip__lt=datetime.now()).order_by("-date_added")
    pt = Trip.objects.exclude(date_of_trip__lt=datetime.now()).extra(select={'entry_count': subq}).order_by('-entry_count')
    dn = Trip.objects.exclude(date_of_trip__lt=datetime.now()).filter(driver__isnull=True).order_by('date_added')

    if cat != None:
        nt = nt.filter(destination__cat=cat)
        pt = pt.filter(destination__cat=cat)
        dn = dn.filter(destination__cat=cat)

    trip_dict['new_trips']  = nt[:5]
    trip_dict['popular_trips'] = pt[:5]
    trip_dict['driver_needed_trips'] = dn[:5]
    trip_dict['user'] = request.user

    return trip_dict

def menu(request):
    """Handle main menu
    Templates:  menu.html
    Called From:    /
                    /rideshare/
    """
    green_feed = cache.get('green_feed')
    if not green_feed:
        green_feed = feedparser.parse('http://news.cnet.com/8300-11128_3-54.xml')
        cache.set('green_feed',green_feed,600)
        
    hint_list = Hints.objects.all()
    num_hints = Hints.objects.count()


    t_data = left_bar_data(request,None)
    t_data['user_count'] = User.objects.count()
    t_data['trip_count'] = Trip.objects.count()
    t_data['headlines'] = green_feed.entries
    t_data['quicksearch'] = QuickSearch()
    t_data['hint'] = hint_list[random.randrange(num_hints)].text
    return render_to_response('menu.html',t_data)

def help(request):
    """ Generates help screen
        Templates:  help.html
        Called From /rideshare/help/
    """
    t_data = left_bar_data(request,None)
    return render_to_response('help.html',t_data)

def contact(request):
    """ Generates contact screen
        Templates:  help.html
        Called From /rideshare/contacts/
    """
    t_data = left_bar_data(request,None)
    return render_to_response('contact.html',t_data)

def create_TripForm(trip_cat):
    """
    Generates a TripForm class dynamically.
    The reason this is generated dynamically is that the autocomplete widget needs to have its
    lookup_url set at the time the class is defined.
    """
    if trip_cat:
        date_required = trip_cat.cat_code != u'commute'
        mycat = trip_cat.cat_code
    else:
        mycat = 'all'
        date_required = True

    class TripForm(forms.Form):
        dest = forms.CharField(widget=AutoCompleteWidget(lookup_url='/rideshare/'+mycat+'/destination_ac/',schema='["resultset.results", "name"]',label="Going to (Place):"))
        dest_city = forms.CharField(widget=AutoCompleteWidget(lookup_url='/rideshare/'+mycat+'/city_ac/',schema='["resultset.results", "name"]', label="In (City):"))
        dest_state = USStateField(label='State:',widget=USStateSelect)
        start_city = forms.CharField(widget=AutoCompleteWidget(lookup_url='/rideshare/'+mycat+'/city_ac/',schema='["resultset.results", "name"]', label="Starting From (City):"))
        start_state = USStateField(label='State:',widget=USStateSelect)
        trip_date = forms.DateField(label="On Date (mm/dd/yy):",required=False)  

        comment = forms.CharField(max_length=500,widget=forms.Textarea,required=False)
        # if mycat != 'all':
        #     trip_cat = forms.CharField(widget=forms.HiddenInput,required=False)
        # else:
        trip_cat = forms.ChoiceField(choices=(('','------------'),('commute','Commute to Work'),('dest','Out of Town'),('event','School Event'),('home','Home')))
    return TripForm


def process_search(request, form, trip_cat):
    """ New form processing to more close match the search first verify second paradigm
        Calls:      /rideshare/process_new_trip/
                    /rideshare/finalize_exact_match/
        Templates:  select_from_list.html
        
        Called By:  add_trip   ---  add_trip.html
    """
    td = form.cleaned_data['trip_date']
    dsn = form.cleaned_data['dest_state'].upper()
    ssn = form.cleaned_data['start_state'].upper()
    dcn = form.cleaned_data['dest_city'].capitalize()
    scn = form.cleaned_data['start_city'].capitalize()
    dname = form.cleaned_data['dest']
    dc,created = City.objects.get_or_create(city_name__iexact=dcn,
                                           state__iexact=dsn,
                                           defaults={'city_name':dcn,'state':dsn})

    sc,created = City.objects.get_or_create(city_name__iexact=scn,
                                        state__iexact=ssn,
                                        defaults={'city_name':scn,'state':ssn})
    cat = get_category(trip_cat)
    destList = Destination.objects.filter(destination_name__icontains=dname, city=dc, cat=cat)
    tripList = []
    for dest in destList:
        match_trips = Trip.objects.filter(destination=dest,start_point=sc).extra(where=['max_passengers > num_passengers'])
        if cat.cat_code != u'commute' and td:
            match_trips = match_trips.filter(date_of_trip=td)
        if match_trips:
            for t in match_trips:
                tripList.append(t)
        
    num_matches = len(tripList)
    if num_matches == 0:
        # This is a new trip.  Create it without a driver then redisplay form with driver info
        tdata = left_bar_data(request,trip_cat)
        TripForm = create_TripForm(cat)
        # TODO make trip_date required now unless commute
        form = TripForm(initial={'start_city':scn,
                                 'start_state':ssn,
                                 'dest':dname,
                                 'dest_city':dcn,
                                 'dest_state':dsn,
                                 'trip_date':td,
                                 'trip_cat':cat.cat_code,
                                 'comment':form.cleaned_data['comment']
                                 })
        
        tdata['rideform'] = form
        tdata['cat'] = cat
        return render_to_response('process_trip.html',tdata)
    elif num_matches == 1:
        # This is a good match check on driving status and finalize
        trip = tripList[0]
        return HttpResponseRedirect('/rideshare/finalize_exact_match/'+str(trip.id)+'/')
    else:
        # multiple matches display the list and allow them to select or create new
        tdata = left_bar_data(request,trip_cat)
        tdata['trip_list'] = tripList
        return render_to_response('select_from_list.html',tdata)


class DriveForm(forms.Form):
    """ Class for a indicate whether or not they can drive.
    
    """
    drive = forms.BooleanField(label="Check here if you are Driving:",required=False)
    num_passengers = forms.ChoiceField(choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)),label="I can take pasengers:",required=False)
    trip = forms.IntegerField(widget=forms.HiddenInput)

# todo make trip category always valid but with proper filled in value
def process_new_trip(request):
    """ 
    Templates:  confirm_trip.html
    
    Calls:  process_search
            finalize_exact_match
            
    Called By:
    """
    if request.method == 'POST':
        cat = get_category(request.POST['trip_cat'])
        TripForm = create_TripForm(cat)
        form = TripForm(request.POST)
        if not cat or cat.id != 1:
            form['trip_date'].field.required = True
        if form.is_valid():
            if form.data['submit'] == 'Create New':
                trip = new_trip_from_form(form,cat)
                trip.save()
                return HttpResponseRedirect('/rideshare/finalize_exact_match/'+str(trip.id)+'/')
            else:
                # search again
                return process_search(request,form,form.cleaned_data['trip_cat'])
        else:
            t_data = left_bar_data(request,cat)
            if not cat:
                t_data['newtrip'] = True
            else:
                t_data['cat'] = cat
            t_data['rideform'] = form
            return render_to_response('process_trip.html', t_data)
    else:
        print 'This form should always be called due to a post'
        

@login_required
def finalize_exact_match(request, trip_id=None):
    """ 
    Templates:  confirm_matching_trip
    
    Calls:      /rideshare/add_trip/newdriver/  -- showriders
                /rideshare/add_trip/notify/
                
    Called by:  process_search    -- add_trip.html
    """

    if request.method == 'POST':
        form = DriveForm(request.POST)
        if form.is_valid():
            trip = Trip.objects.get(id=form.cleaned_data['trip'])
            willDrive = form.cleaned_data['drive']
            
            if willDrive and not trip.driver:
                trip.driver = request.user
                trip.max_passengers = form.cleaned_data['num_passengers']
                trip.save()
                return HttpResponseRedirect('/rideshare/add_trip/newdriver/'+str(trip.id)+'/')
            elif willDrive and trip.driver:
                trip = Trip(destination=trip.destination,start_point=trip.start_point,date_of_trip=trip.date_of_trip,driver=request.user,comment=trip.comment)
                trip.max_passengers = form.cleaned_data['num_passengers']                
                trip.save()
                return HttpResponseRedirect('/rideshare/add_trip/newdriver/'+str(trip.id)+'/')
            elif trip.driver:
                trip.requests.add(request.user)
                email_driver(request.user,trip)
                return HttpResponseRedirect('/rideshare/add_trip/driver_notify/')                
            else:
                trip.requests.add(request.user)
                return HttpResponseRedirect('/rideshare/add_trip/notify/')
        else:
            return render_to_response('confirm_matching_trip.html',{'form':form}) # should always validate
    else:
        trip = Trip.objects.get(id=trip_id)
        tdata = left_bar_data(request,trip.destination.cat)
        tdata['trip'] = trip
        #print "REFERER: ", request.META['HTTP_REFERER']
        #if "newtrip" in request.META['HTTP_REFERER']:
        tdata['greet'] = 'The details of your trip are:'
        #else:
        #    tdata['greet'] = 'We found one trip that matches your request:'

        drive_form = DriveForm(initial={'trip':trip.id})
        tdata['form'] = drive_form
        return render_to_response('confirm_matching_trip.html',tdata)
    

def get_category(key):
    CAT_MAP = {'commute':1,'event':2,'dest':3,'home':4,'all':None, '':None}
    if isinstance(key,unicode):
        idnum = CAT_MAP[key]
        if idnum:
            return Category.objects.get(id=CAT_MAP[key])
        else:
            return None
    elif isinstance(key,Trip):
        return key.destination.cat
    elif isinstance(key,Category):
        return key
    elif key == None:
        return None
    else:
        print key, "is not understood"

@login_required
def add_trip(request,trip_cat):
    """ Add a new trip
        The TripForm class is defined inside this method so that Citys and Destinations
        are up to date.  If it was defined outside it would only contain the cities on 
        the list when the server was started.
        
    Templates:  add_trip.html
    
    Calls:      process_search
    
    Called_by:  /rideshare/newtrip/<trip_cat>/
    """
    
    t_data = left_bar_data(request,trip_cat)

    cat = get_category(trip_cat)

    t_data['cat'] = cat
    TripForm = create_TripForm(cat)
    
    t_data['request'] = trip_cat  # cat.cat_code

    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            return process_search(request,form,trip_cat)
        else:
            t_data['rideform'] = form
            return render_to_response('add_trip.html', t_data)
    else:
        t_data['rideform'] = TripForm(initial={'start_city':'Decorah', 'start_state':'IA', 'dest_state':'IA','trip_cat':cat.cat_code})
        return render_to_response('add_trip.html', t_data)


@login_required
def quicksearch(request):
    """search city and destination"""
    t_data = left_bar_data(request,None)
    if request.method == 'POST':
        form = QuickSearch(request.POST)
        if form.is_valid():
            trip_list = find_matching_rides(form.cleaned_data['terms'])
            t_data['trip_list'] = trip_list
            if len(trip_list) > 0:
                return render_to_response('select_from_list.html',t_data)
            else:
                FormClass = create_TripForm(None)
                form = FormClass(initial={'start_state':'IA', 'dest_state':'IA'})
                t_data['rideform'] = form
                t_data['newtrip'] = True
                return render_to_response('process_trip.html', t_data)

        else:
            return menu(request)

        

def find_matching_rides(terms):
    term_list = terms.split()

    dest_desc_results = Trip.objects.filter(Q(destination__destination_name__icontains = term_list[0])|Q(destination__city__city_name__icontains = term_list[0])).exclude(date_of_trip__lt=datetime.now())
    for term in term_list[1:]:
        dest_desc_results = dest_desc_results & Trip.objects.filter(Q(destination__destination_name__icontains = term)|Q(destination__city__city_name__icontains = term)).exclude(date_of_trip__lt=datetime.now())

    return dest_desc_results

# TODO Implement a more secure method of accept decline that does not put the userid and tripid in the open
@login_required
def add_rider(request, trip_id, rider_id):
    """docstring for add_rider"""
    trip = Trip.objects.get(id=trip_id)
    rider = User.objects.get(id=rider_id)
    trip.riders.add(rider)
    trip.num_passengers += 1
    trip.save()
    trip.requests.remove(rider)
    notify_rider(rider,trip)
    return render_to_response('rider_added.html',{'rider':rider,'trip':trip})

# TODO Add drivers name to pool for free gas card?

@login_required    
def decline_rider(request, trip_id, rider_id):
    """docstring for decline_rider"""
    trip = Trip.objects.get(id=trip_id)
    rider = User.objects.get(id=rider_id)
    trip.requests.remove(rider)
    # If there is another trip available put the rider on the request list.
    # If there is not another trip available then make one with a driver needed
    trip_list = Trip.objects.filter(destination=trip.destination,date_of_trip=trip.date_of_trip,start_point=trip.start_point).exclude(driver=trip.driver)
    if len(trip_list) > 0:
        trip_list[0].requests.add(rider)
        email_driver(rider,trip)
    else:
        trip = Trip(destination=trip.destination,date_of_trip=trip.date_of_trip,start_point=trip.start_point,comment=trip.comment)
        trip.save()
        trip.requests.add(rider)
    return render_to_response('rider_declined.html',{'rider':rider, 'trip':trip})


# TODO Convert email to include html... see: http://www.djangoproject.com/documentation/email/
def notify_rider(rider,trip):
    """Compose a message and send it to a rider to let them know they have a ride."""
    email_context = {'trip':trip, 'rider':rider}
    message = render_to_string('rider_notify_email.txt', email_context)
    send_mail(
        'Ride Notification from DecorahRideshare.com',
        message,
        settings.DEFAULT_FROM_EMAIL,
        [rider.email],
        fail_silently=False
    )
    
def email_driver(rider,trip):
    """docstring for email_driver"""
    current_site = Site.objects.get_current()
    email_context = {'trip':trip, 'rider':rider, 'site':current_site}
    message = render_to_string('driver_request_email.txt',email_context)
    send_mail(
        'Ride Request from DecorahRideshare.com',
        message,
        settings.DEFAULT_FROM_EMAIL,
        [trip.driver.email],
        fail_silently=False
    )

# New driver and New trip
def thanks(request):
    return render_to_response('add_trip_success.html',left_bar_data(request,None))

# New trip, but no driver
def driver_needed(request):
    """docstring for driver_needed"""
    return render_to_response('add_trip_need_driver.html',left_bar_data(request,None))

# Old Trip new driver
def showriders(request,trip_id):
    """docstring for showriders"""
    print 'in showriders'
    trip = Trip.objects.get(id=trip_id)
    t_data = left_bar_data(request,get_category(trip))    
    riders = trip.requests.all()
    rl = [(r.id, r.first_name+' '+r.last_name) for r in riders]
    t_data['riders'] = riders
    
    class SelectRiders(forms.Form):
        rider_list = forms.MultipleChoiceField(rl,widget=forms.CheckboxSelectMultiple)

    if request.method == 'POST':
        print 'POSTED'
        form = SelectRiders(request.POST)
        if form.is_valid():
            selected_riders = form.cleaned_data['rider_list']
            for rider in selected_riders:
                rider = User.objects.get(id=rider)
                trip.requests.remove(rider)
                trip.riders.add(rider)
                trip.num_passengers += 1
                trip.save()
                notify_rider(rider,trip)
        else:
            print 'form did not validate'
        return HttpResponseRedirect('/rideshare/add_trip/success/')
    else:
        print 'NOT POSTED'
        form = SelectRiders()
        t_data['form'] = form
        t_data['user'] = request.user
        t_data['trip'] = trip
        return render_to_response('add_trip_showriders.html',t_data)


# Old Trip, new request for ride
def waitfordriver(request):
    """docstring for waitfordriver"""
    return render_to_response('add_trip_driver_notify.html',left_bar_data(request,None))

@login_required
def get_my_trips(request):
    """docstring for get_my_trips"""
    #my_trips = Trip.objects.filter(driver=request.user)
    me = request.user
    my_trips = Trip.objects.filter(Q(driver=me)|Q(requests=me)|Q(riders=me)).exclude(date_of_trip__lt=datetime.now()).order_by('date_of_trip')
    t_data = left_bar_data(request,None)
    t_data['my_trips'] = my_trips
    return  render_to_response('my_trips.html',t_data)
    
#
class UpdateTripForm(forms.Form):
    """ Class for a indicate whether or not they can drive.
    
    """
    drive = forms.BooleanField(label="Check here if you are Driving:",required=False)
    remove_me = forms.BooleanField(label="I am no longer interested in this trip",required=False)    
    num_passengers = forms.ChoiceField(choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)),label="I can take pasengers:",required=False)

    
    
@login_required
def edit_trip(request,trip_id):
    """docstring for get_my_trips"""
    me = request.user
    t_data = left_bar_data(request,None)
    my_trip = Trip.objects.get(id=trip_id)
    t_data['num_riders'] = my_trip.riders.count()
    t_data['num_requests'] = my_trip.requests.count()
    if my_trip.driver == me:
        t_data['type'] = 'driver'
    elif my_trip.riders.filter(username=me.username):
        t_data['type'] = 'rider'
    else:
        t_data['type'] = 'request'
    print 'type = ', t_data['type']
    if request.method == 'POST':
        if t_data['type'] == 'driver':
            TripForm = create_TripForm(my_trip.destination.cat)
            form = TripForm(request.POST)
            if form.is_valid():
                return update_trip(request,form,my_trip,me)
            else:
                t_data['rideform'] = form
                t_data['cat'] = my_trip.destination.cat
                return render_to_response('edit_trip.html',t_data)
        elif t_data['type'] == 'rider' or t_data['type'] == 'request':
            form = UpdateTripForm(request.POST)
            if not form.is_valid():
                t_data['form'] = form
                return render_to_response('edit_ride_status.html',t_data)
            if form.cleaned_data['remove_me']:
                my_trip.riders.remove(me)
                my_trip.requests.remove(me)
                return HttpResponseRedirect('/rideshare/edit_success')
            elif form.cleaned_data['drive']:
                my_trip.riders.remove(me)
                my_trip.requests.remove(me)                
                if not my_trip.driver:
                    my_trip.driver = me
                    my_trip.max_passengers = form.cleaned_data['num_passengers']                
                    my_trip.save()
                    trip=my_trip
                else:
                    trip = Trip(destination=my_trip.destination,start_point=my_trip.start_point,date_of_trip=my_trip.date_of_trip,driver=me,comment=my_trip.comment)
                    trip.max_passengers = form.cleaned_data['num_passengers']                
                    trip.save()
                return HttpResponseRedirect('/rideshare/add_trip/newdriver/'+str(trip.id)+'/')                
        else:
            print 'no other options here'

        return HttpResponseRedirect('/rideshare/edit_success')
    else:
        t_data['trip'] = my_trip
        if t_data['type'] == 'driver':
            TripForm = create_TripForm(my_trip.destination.cat)
            t_data['rideform'] = TripForm(initial={'start_city':my_trip.start_point.city_name,
                                     'start_state':my_trip.start_point.state,
                                     'dest':my_trip.destination.destination_name,
                                     'dest_city':my_trip.destination.city.city_name,
                                     'dest_state':my_trip.destination.city.state,
                                     'trip_date':my_trip.date_of_trip,
                                     'trip_cat':my_trip.destination.cat.cat_code,
                                     'comment':my_trip.comment
                                     })
            t_data['cat'] = my_trip.destination.cat
            return render_to_response('edit_trip.html',t_data)
        else:
            t_data['form'] = UpdateTripForm()
            return render_to_response('edit_ride_status.html',t_data)


def update_trip(request,form,trip,me):
    """update_trip handles the case where the driver for the trip wants to either
       cancel the trip or modify some details."""

    print 'in update_trip'
    if form.data['submit'] == 'Cancel Trip':
        print 'cancelling trip'
        if trip.riders.count() == 0 and trip.requests.count() == 0:
            trip.delete()
            return HttpResponseRedirect('/rideshare/trip_deleted/')
        else:
            trip.driver = None
            notify_riders_no_driver(trip)
            trip.save()
            return HttpResponseRedirect('/rideshare/driver_removed/')
    else:
        if trip.riders.count() == 0 and trip.requests.count() == 0:
            driver = trip.driver
            trip.delete()
            trip = new_trip_from_form(form,trip.destination.cat)
            trip.driver = driver
            trip.save()
        else:
            newtrip = new_trip_from_form(form,trip.destination.cat)
            trip.driver = None
            notify_riders_no_driver(trip)
            newtrip.save()
        return HttpResponseRedirect('/rideshare/trip_updated/')

def notify_riders_no_driver(trip):
    """Riders for this trip no longer have a driver."""
    for rider in trip.riders.all():
        email_context = {'trip':trip, 'rider':rider}
        message = render_to_string('trip_change_email.txt', email_context)
        send_mail(
            'Ride Notification from DecorahRideshare.com',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rider.email],
            fail_silently=False
        )
        
        
def new_trip_from_form(form,cat):
    """docstring for new_trip_from_form"""
    td = form.cleaned_data['trip_date']
    dsn = form.cleaned_data['dest_state'].upper()
    ssn = form.cleaned_data['start_state'].upper()
    dcn = form.cleaned_data['dest_city'].capitalize()
    scn = form.cleaned_data['start_city'].capitalize()
    dname = form.cleaned_data['dest']
    comtext = form.cleaned_data['comment']
    dc,created = City.objects.get_or_create(city_name__iexact=dcn,
                                           state__iexact=dsn,
                                           defaults={'city_name':dcn,'state':dsn})

    sc,created = City.objects.get_or_create(city_name__iexact=scn,
                                        state__iexact=ssn,
                                        defaults={'city_name':scn,'state':ssn})

    dest,created = Destination.objects.get_or_create(destination_name=dname,city=dc,cat=cat)
    trip = Trip(destination=dest,start_point=sc,date_of_trip=td,comment=comtext)
    return trip
    

def edit_success(request):
    """docstring for edit_success"""
    t_data = left_bar_data(request,None)
    return render_to_response('edit_success.html',t_data)
    
    
def trip_deleted(request):
    """docstring for trip_deleted"""
    t_data = left_bar_data(request,None)
    return render_to_response('trip_deleted.html',t_data)
    
def driver_removed(request):
    """docstring for driver_removed"""
    t_data = left_bar_data(request,None)
    return render_to_response('driver_removed.html',t_data)

def trip_updated(request):
    """docstring for trip_updated"""
    t_data = left_bar_data(request,None)
    return render_to_response('trip_updated.html',t_data)

#
#   Ajax Autocomplete functions
#

def destination_ac(request,trip_cat):
    """ returns data displayed at autocomplete list - this function is accessed by AJAX calls
    """
    limit = 10
    query = request.GET.get('query', None)
    qargs = []
    print 'in destination_ac'
    if query:
        dests = Destination.objects.filter(destination_name__icontains = query).order_by('destination_name')
        if trip_cat != 'all':
            cid = get_category(trip_cat)
            dests = dests.filter(cat=cid)
        results = []
        for d in dests:
            results.append({'id':d.id, 'name':d.destination_name})
    ret_dict = {'resultset':{'totalResultsReturned':len(results),
                             'results':results}}

    return JsonResponse(ret_dict)

def city_ac(request,cat):
    """docstring for city_ac"""
    query = request.GET.get('query',None)
    print 'city_ac q = ', query
    if query:
        cities = City.objects.filter(city_name__icontains = query).order_by('city_name')
        results = []
        for d in cities:
            results.append({'id':d.id, 'name':d.city_name, 'state':d.state})
    ret_dict = {'resultset':{'totalResultsReturned':len(results),
                             'results':results}}
    return JsonResponse(ret_dict)


##
## My Admin Reports
##

@login_required
def alltrips(request):
    """docstring for waitfordriver
    Called by:  report_all_trips
    """
    tlist = Trip.objects.exclude(date_of_trip__lt=datetime.now()).order_by("-date_of_trip")
    return render_to_response('all_trips.html',{'all_trips':tlist})

def allusers(request):
    """docstring for waitfordriver
    Called by:  report_all_trips
    """
    if request.user.is_superuser:
        userlist = User.objects.all().order_by("-date_joined")[:100]
        return render_to_response('all_users.html',{'all_users':userlist})

#
#   Forms
#


class ConfirmDrive(forms.Form):
    drive = forms.ChoiceField(choices=((1, 'Yes, I will drive and take additional riders'),(2,'I would prefer ride with the existing driver')),widget=forms.RadioSelect)
    trip = forms.IntegerField(widget=forms.HiddenInput)


class RideShareRegister(RegistrationForm):
    first_name = forms.CharField(max_length=30,label=u'First Name')
    last_name = forms.CharField(max_length=30,label=u'Last Name')


    def save(self, profile_callback=None):
        """
        Creates the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    first_name=self.cleaned_data['first_name'],
                                                                    last_name=self.cleaned_data['last_name'],
                                                                    profile_callback=profile_callback)
        return new_user

class QuickSearch(forms.Form):
        terms = forms.CharField(max_length=30,label=u'Quick Search')
