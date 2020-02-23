import random
import datetime
from datetime import date,timedelta
import time
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.template import loader

from django.db.models import Exists, OuterRef, Q, Count
from django.db.models.functions import Lower
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin,AccessMixin
from django.contrib.auth import get_user_model
from django.views import generic
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
import django_filters
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django_ajax.decorators import ajax
from django_ajax.mixin import AJAXMixin
from catalog.forms import *
from catalog.models import Music, Composer, MusicInstance, Genre, MusicInstanceReservation,ActivityLog,Review
from pprint import pprint
#from rest_framework import serializers

def is_in_group(user,group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

# The home page will depend on the logged in user and which group they belong to
class HomePageView(TemplateView):
    def get_template_names(self):
        if  not self.request.user.is_authenticated:
            return "visitorindex.html"
        if is_in_group(self.request.user,"Nonmember"):
            return "nonmemberindex.html"
        if is_in_group(self.request.user,"Librarian"):
            return "librarianindex.html"
        if is_in_group(self.request.user,"Member"):
            return "memberindex.html"
        return super().get_template_names()
    template_name = 'index.html'
# calendarStartDate event_list
    '''
      {
          title: 'All Day Event',
          start: '2020-02-01'
        },
        {
          title: 'Long Event',
          start: '2020-02-07',
          end: '2020-02-10'
        },
        {
          groupId: '999',
          title: 'Repeating Event',
          start: '2020-02-09T16:00:00'
        },
        {
          groupId: '999',
          title: 'Repeating Event',
          start: '2020-02-16T16:00:00'
        },
        {
          title: 'Conference',
          start: '2020-02-11',
          end: '2020-02-13'
        },
        {
          title: 'Meeting',
          start: '2020-02-12T10:30:00',
          end: '2020-02-12T12:30:00'
        },
        {
          title: 'Lunch',
          start: '2020-02-12T12:00:00'
        },
        {
          title: 'Meeting',
          start: '2020-02-12T14:30:00'
        },
        {
          title: 'Birthday Party',
          start: '2020-02-13T07:00:00'
        },
        {
          title: 'Click for Google',
          url: 'http://google.com/',
          start: '2020-02-28'
        }

    '''


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = None
        # Generate counts of some of the main objects
        num_music = Music.objects.all().count()
        num_instances = MusicInstance.objects.all().count()
        # Available copies of books
        num_instances_available = MusicInstance.objects.filter(status__exact='a').count()
        num_composers = Composer.objects.count()  # The 'all()' is implied by default.
        # Number of visits to this view, as counted in the session variable.
        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits+1
        can_reserve = False
        if self.request.user.has_perm('catalog.can_issue'):
            can_reserve = True
        xxx = (
            {'can_reserve':can_reserve ,'num_music': num_music, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_composers': num_composers,
                 'num_visits': num_visits})
        context.update(xxx)
        context['calendarStartDate'] = date.today().strftime("%Y-%m-%d")
        statusq = Q(status__exact = 'r') | Q(status__exact = 'o')
        if self.request.user.has_perm('catalog.can_any_reserve'):
            instances = MusicInstance.objects.filter(statusq)
        else:
            instances = MusicInstance.objects.filter(statusq, borrower_id = self.request.user.id)
        events = []
        for event in instances:
            eventtext = '{title:" ' + str(event.music.title) + '\\n user: ' + str(event.borrower) + '",start:"' + event.due_back.strftime("%Y-%m-%d") + '"},'
            events.append(eventtext)
            context['event_list'] = events
        return context

    def render_to_response(self,context,**kwargs):
        return super().render_to_response(context);

# These next views are the various ways of seeing our data
class MusicListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view for a list of music."""
    model = Music
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
        
    def has_permission(self):
        if not self.request.user.is_authenticated:
           print("musiclistview not authenticated")
           return False
        if not self.request.user.has_perm('catalog.can_browse_catalog'):
           print("musiclistview user lacks can_browse_catalog")
           return False    
        return True       

class MusicListGridView(PermissionRequiredMixin,TemplateView):
    """Generic class-based view for a list of music."""
    template_name = "catalog/music_list_grid.html"
    def has_permission(self):
        if not self.request.user.is_authenticated:
           print("musiclistview not authenticated")
           return False
        if not self.request.user.has_perm('catalog.can_browse_catalog'):
           print("musiclistview user lacks can_browse_catalog")
           return False    
        return True       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #queryjson = serializers.serialize('json',music.objects().all())
        x = list(Music.objects.values('id','title','composer__last_name','genre__name','language__name').order_by(Lower('composer__last_name')))
        queryjson = json.dumps(x)
        
        context['queryjson'] = queryjson
        return context
     

class MusicDetailView(PermissionRequiredMixin,generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Music
    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('catalog.can_browse_catalog'):
           return False    
        return True
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        music=kwargs['object']
        print(music)
        available=music.musicinstance_set.filter(status__exact = 'a')
        navailable = available.count()
        context['music'] = music
        context['firstavailable'] = available.first()
        context['navailable'] = navailable
        context['show_reserve_button'] = navailable > 0 and (self.request.user.has_perm('catalog.can_self_reserve') or self.request.user.has_perm('catalog.can_any_reserve'))
        context['form'] = GetUserForm(initial={'user': self.request.user})
        return context

# Clean up composer just like we did for music
class ComposerListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Composer
    paginate_by = 10

    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_browse_catalog'):
            return False
        return True

class ComposerDetailView(generic.DetailView):
    """Generic class-based detail view for a composer """
    model = Composer

class BorrowedOrReservedByUser(PermissionRequiredMixin, generic.ListView):
    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('catalog.can_self_reserve'):
           return False
        return True
    template_name = "catalog/borrowed_or_reserved_by_user.html"
    context_object_name = 'instances'
    paginate_by = 10
    def get_queryset(self, **kwargs):
        statusq = Q(status__exact = 'r') | Q(status__exact = 'o')
        instances = MusicInstance.objects.filter(statusq, borrower_id = self.request.user.id)
        '''for i in instances:
            if instance.statusq == 'r' and (date.today() - instance.due_back) < 0:
           '''  
        return instances
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context    
    
class BorrowedOrReservedByAll(PermissionRequiredMixin, generic.ListView):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_any_reserve'):
            return False
        return True
    template_name = "catalog/borrowed_or_reserved_by_all.html"
    context_object_name = 'instances'
    paginate_by = 10
    def get_queryset(self, **kwargs):
        statusq = Q(status__exact = 'r') | Q(status__exact = 'o')
        instances = MusicInstance.objects.filter(statusq)
        return instances
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context 
import json
class BorrowedPie(PermissionRequiredMixin,TemplateView):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_any_reserve'):
            return False
        return True
    template_name = "catalog/borrowed_pie.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history = ActivityLog.objects.filter(activityCode='bor').values('music__title','music__composer__last_name','activityCode').annotate(events=Count('id')).order_by('-events')
        chartDataArray = []
        for record in history:
            dict = {}
            dict['x'] =  record['music__title'] + ' ' + record['music__composer__last_name'] + ' ' + record['activityCode']
            dict['value'] = str(record['events'])
            chartDataArray.append(dict)
        context['chartData'] = json.dumps(chartDataArray)
        ''' [
        {x: "Beethoven", value: 25},
        {x: "Williams", value: 8},
        {x: "Mozart", value: 12},
        {x: "Bruch", value: 11},
         ];
        '''
        return context 



class BorrowedList(PermissionRequiredMixin,TemplateView):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_any_reserve'):
            return False
        return True
    template_name = "catalog/borrowed_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history = ActivityLog.objects.filter(activityCode='bor').values('music__title','music__composer__last_name','activityCode').annotate(events=Count('id')).order_by('-events')
        chartDataArray = []
        for record in history:
            row = [ record['music__title'] + ' ' + record['music__composer__last_name'],record['events'] ]
            chartDataArray.append(row)
        context['chartData'] = json.dumps(chartDataArray)
        return context 

# Now the post actions
class ReserveAction(PermissionRequiredMixin,FormView) :   
    template_name = 'catalog/music_detail.html'
    form_class = GetUserForm
    success_url = '/catalog/feedback'

    def get_context_data(self, **kwargs):
        print('ReserveAction getcontextdata')
        context = super().get_context_data(**kwargs)
        whichCopy= self.request.POST['reservebutton']
        print('Reserve action copy is ' + str(whichCopy))
        context['music'] =  MusicInstance.objects.get(id = whichCopy).music
        return context 

    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('catalog.can_self_reserve'):
            if not self.request.user.has_perm('catalog.can_any_reserve'):
               return False
        return True

    def form_valid(self, form):
        request = self.request
        print("form reserveAction is valid")
        whichCopy= request.POST['reservebutton']
        instance = MusicInstance.objects.get(id = whichCopy)
        user=form.cleaned_data['user']
        reservationnumber,instance = instance.reserve(user) #dateOverride= to override the date here
        emailAddress= request.user.email
        send_mail(
            'Music Reserved',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        messages.info(self.request,"Reservation successful: Your reservation number is %s" % (reservationnumber))
        return super().form_valid(form)

    def postNotUsed(self,request,*args,**kwargs):
        whichCopy= request.POST['reservebutton']
        instance = MusicInstance.objects.get(id = whichCopy)

        reservationnumber,instance = instance.reserve(request.user) #dateOverride= to override the date here
        emailAddress= request.user.email
        send_mail(
            'Music Reserved',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        messages.info(self.request,"Reservation successful: Your reservation number is %s" % (reservationnumber))
        return HttpResponseRedirect("/catalog/feedback")

class CancelReserveAction(PermissionRequiredMixin, View):
    def has_permission(self):
         if not self.request.user.is_authenticated:
             return False
         if not self.request.user.has_perm('catalog.can_self_reserve'):
             return False
         return True
    def post(self,request,*args,**kwargs):
        whichCopy= request.POST['cancelReservation']
        instance = MusicInstance.objects.get(id = whichCopy)
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = False, returned = False, cancelled = False)
        reservationnumber = reservation.borrowedid
        reservation.cancel(request.user)
        emailAddress= request.user.email
        send_mail(
            'Music Reservation has been cancelled',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        messages.info(self.request,"Reservation number  %s has been cancelled" % (reservationnumber))
        return HttpResponseRedirect("/catalog/feedback")

class BorrowInstanceAction(PermissionRequiredMixin, View):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_issue'):
            return False
        return True
    def post(self, request, *args, **kwargs):
        whichCopy = request.POST['instanceId']
        instance = MusicInstance.objects.get(id = whichCopy)
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = False, cancelled = False)
        instance=reservation.borrow(request.user)

        userid = reservation.userid_id
        user = User.objects.get(id = str(userid))
        reservationnumber = reservation.borrowedid
        email = user.email
        send_mail(
            'Music Borrowed',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [email])
        messages.info(self.request, "The borrowing was successful: %s has borrowed %s" % (user, whichCopy))
        return HttpResponseRedirect("/catalog/feedback")

class RenewInstanceAction(PermissionRequiredMixin, View):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_issue'):
            return False
        return True

    def post(self,request,*args,**kwargs):
        whichCopy = request.POST['instanceId']
        instance = MusicInstance.objects.get(id = whichCopy)
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = True, returned = False)
        reservation.renew(request.user)
        
        userid = reservation.userid_id
        user = User.objects.get(id = str(userid))
        email = user.email
        send_mail(
            'Music Returned',
            'Your reservation: ' + str(id) +' has been returned',
            'adam@Bilkus.com',
            [email])
        messages.info(self.request, "Return Successful: %s has returned %s" % (user, whichCopy))
        return HttpResponseRedirect("/catalog/feedback")

class ReturnInstanceAction(PermissionRequiredMixin, View):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_issue'):
            return False
        return True

    def post(self,request,*args,**kwargs):
        whichCopy = request.POST['instanceId']
        instance = MusicInstance.objects.get(id = whichCopy)
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = True, returned = False, cancelled=False)
        user = reservation.returns(request.user)
        email = user.email
        send_mail(
            'Music Returned',
            'Your reservation: ' + str(id) +' has been returned',
            'adam@Bilkus.com',
            [email])
        messages.info(self.request, "Return Successful: %s has returned %s" % (user.id, whichCopy))
        return HttpResponseRedirect("/catalog/reviewMusic/" + str(reservation.id))

class RoutineMaintenance(PermissionRequiredMixin,View):
    def has_permission(self):
        if not self.request.user.is_superuser:
            return False
        return True
    def get(self,request,*args,**kwargs):
        MusicInstanceReservation.cancelExpiredReservations(request.user)
        return HttpResponse("Routine maintenance has run")

class ReviewMusic(FormView):
    template_name = 'catalog/review_music.html'
    form_class = ReviewMusicForm
    success_url = '/catalog/feedback'

    def form_valid(self, form):
        musicreservationkey=self.kwargs['pk']
        musicreservation=MusicInstanceReservation.objects.get(id=musicreservationkey)
        music = musicreservation.musicInstance.music
        user = musicreservation.userid
        rating=form.cleaned_data['rating']
        if rating == 0:
            messages.warning(self.request,"You chose not to review this item - please do so in future!")
            return super().form_valid(form)    
        review = Review(user=user,music=music,rating=rating)
        review.save()
        messages.info(self.request,'Thank you for your rating')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        musicreservationkey=self.kwargs['pk']
        musicreservation=MusicInstanceReservation.objects.get(id=musicreservationkey)
        music = musicreservation.musicInstance.music
        user = musicreservation.userid
        context['music'] = music
        context['user'] = user
        context['reservation'] = musicreservation
        return context

class CreateRandomMusic(PermissionRequiredMixin,View):
    def has_permission(self):
         if not self.request.user.is_superuser:
             return False
         return True
    def get(self,request,*args,**kwargs):
        items = ['Symphony no: 3','Bagatelle in G','Minuet and Rondo','Concerto for Strings']
        allComposers = Composer.objects.all()
        for composer in allComposers:
            print("creating random music for %s" % (composer.last_name))
            for itemname in items:
                m = Music(
                title = itemname,
                composer = composer,
                summary = 'Automatically generated',
                barcode = '12345')
                m.save()
        return HttpResponse("Random music created")
class CreateRandomMusicInstances(PermissionRequiredMixin,View):
    def has_permission(self):
         if not self.request.user.is_superuser:
             return False
         return True
    def get(self,request,*args,**kwargs):
        allMusic = Music.objects.all()
        for music in allMusic:
            for i in random.choice(range(1,5)):
                print('Creating %d instances for %s' % (i,music.title))
                m = MusicInstance(
                    music=music
                )
                m.save()
        return HttpResponse("Random music created")

class CreateRandomReviews(PermissionRequiredMixin,View):
    def has_permission(self):
        if not self.request.user.is_superuser:
            return False
        return True
    def get(self,request,*args,**kwargs):
        allMusic = Music.objects.all()
        for userid in range(6,9): # member1 is user id 6
            for music in allMusic:
                myRating = random.choice(range(-3,11))
                if myRating < 1:
                    continue
                newRating = Review(user_id=userid,music=music,rating=myRating)
                newRating.save()
                print("Saved rating for music id " + str(music.id))
        return HttpResponse("Random reviews created ")

class CreateRandomGenre(PermissionRequiredMixin,View):
    def has_permission(self):
         if not self.request.user.is_superuser:
             return False
         return True
    def get(self,request,*args,**kwargs):
        choices = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        for i in range(0,20):
            print("creating random genre")
            genre = ""
            tempgenre = []
            for letters in range(0,random.randint(4, 201)):
                letter = random.choice(choices)
                tempgenre.append(letter)
            for x in tempgenre:
                genre += x
            m = Genre(
            name = genre)
            m.save()
        return HttpResponse("Random genre created")
class AssignRandomGenre(PermissionRequiredMixin,View):
    def has_permission(self):
        if not self.request.user.is_superuser:
            return False
        return True
    def get(self,request,*args,**kwargs):
        allMusic = Music.objects.all()
        allGenre = Genre.objects.all()
        for music in allMusic:
            genre = random.choice(allGenre)
            if music.genre != None:
                continue
            music.genre = genre
            music.save()
            print("Saved genre for music id " + str(music.id))
        return HttpResponse("Random genre assigned")
class FeedbackView(TemplateView):
    template_name = 'catalog/feedback.html'

class SuggestionsView(PermissionRequiredMixin,TemplateView):
    template_name = 'catalog/suggestions.html'
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_self_reserve'):
            return False
        return True
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userId =self.kwargs['pk']
        user = User.objects.get(id=userId)
        context['suggestions'] = Review.suggestionsForUser(user)
        context['user'] = user
        return context        
'''
class ComposerCreate(CreateView):
    model = Composer
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class ComposerUpdate(UpdateView):
    model = Composer
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class ComposerDelete(DeleteView):
    model = Composer
    success_url = reverse_lazy('composers')

class MusicCreate(CreateView):
    model = Music
    fields = '__all__'

class MusicUpdate(UpdateView):
    model = Music
    fields = '__all__'

class MusicDelete(DeleteView):
    model = Music
    success_url = reverse_lazy('musics')

class MusicFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = Music
        fields = ['genre', 'language']


'''
