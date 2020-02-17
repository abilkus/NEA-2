import random
import datetime
from datetime import date
import time
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.template import loader
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Q
from datetime import timedelta
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
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django_ajax.decorators import ajax
from django_ajax.mixin import AJAXMixin
from catalog.forms import RenewMusicForm
from catalog.models import Music, Composer, MusicInstance, Genre, MusicInstanceReservation,ActivityLog

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
        if self.request.user.has_perm('catalog.can_self_reserve'):
            can_reserve = True
        xxx = (
            {'can_reserve':can_reserve ,'num_music': num_music, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_composers': num_composers,
                 'num_visits': num_visits})
        context.update(xxx)
        context['calendarStartDate'] = date.today().strftime("%Y-%m-%d")
        statusq = Q(status__exact = 'r') | Q(status__exact = 'o')
        instances = MusicInstance.objects.filter(statusq, borrower_id = self.request.user.id)
        events = []
        for event in instances:
            eventtext = '{title:" ' + str(event.music.title) + '",user:"' + str(event.borrower) + '",start:"' + event.due_back.strftime("%Y-%m-%d") + '"},'
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

class ActivityChart(PermissionRequiredMixin,TemplateView):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_any_reserve'):
            return False
        return True
    template_name = "catalog/activity_chart.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context 

# Now the post actions
class ReserveAction(PermissionRequiredMixin,View) :     
    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('catalog.can_self_reserve'):
            if not self.request.user.has_perm('catalog.can_any_reserve'):
               return False
        return True
  
    def post(self,request,*args,**kwargs):
        whichCopy= request.POST['reservebutton']
        reservationnumber = get_random_string(length=6, allowed_chars='1234567890')
        reservationnumber = int(reservationnumber)
        instance = MusicInstance.objects.get(id = whichCopy)
        instance.status = 'r'
        instance.due_back = datetime.date.today() + timedelta(days=122)
        instance.borrower = request.user
        instance.save()
        emailAddress= request.user.email
        print(emailAddress)
        reservation = MusicInstanceReservation(borrowedid = reservationnumber, musicInstance=instance , takenoutdate = date.today(), userid=request.user)
        activity = ActivityLog(activityCode = 'res', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=request.user)
        activity.save()
        reservation.save()
        send_mail(
            'Music Reserved',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        messages.info(self.request,"Reservation successful: Your reservation number is %s" % (reservationnumber))
        return HttpResponseRedirect("/catalog")

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
        instance.status = 'a'
        instance.due_back = None
        instance.borrower = None
        instance.save()
        emailAddress= request.user.email
        print(emailAddress)
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = False, returned = False, cancelled = False)
        reservationnumber = reservation.borrowedid
        reservation.cancelled = True
        reservation.save()
        send_mail(
            'Music Reservation has been cancelled',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        messages.info(self.request,"Reservation number  %s has been cancelled" % (reservationnumber))
        return HttpResponseRedirect("/catalog/borrowedOrReservedByUser")

class borrowInstanceAction(PermissionRequiredMixin, View):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_issue'):
            return False
        return True
    def post(self, request, *args, **kwargs):
        whichCopy = request.POST['instanceId']
        instance = MusicInstance.objects.get(id = whichCopy)
        instance.status = 'o'
        instance.due_back = date.today() + timedelta(days = 42)
        instance.save()
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = False, cancelled = False)
        reservation.due_back = instance.due_back
        reservation.takenout = True
        reservation.takenoutdate = date.today()
        reservation.returned = False
        reservation.save()
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
        return HttpResponseRedirect("/catalog")

class renewInstanceAction(PermissionRequiredMixin, View):
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
        reservation.due_back = date.today() + timedelta(days = 42)
        id = reservation.borrowedid
        reservation.save()
        userid = reservation.userid_id
        user = User.objects.get(id = str(userid))
        email = user.email
        send_mail(
            'Music Returned',
            'Your reservation: ' + str(id) +' has been returned',
            'adam@Bilkus.com',
            [email])
        messages.info(self.request, "Return Successful: %s has returned %s" % (user, whichCopy))
        return HttpResponseRedirect("/catalog")

class returnInstanceAction(PermissionRequiredMixin, View):
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('catalog.can_issue'):
            return False
        return True

    def post(self,request,*args,**kwargs):
        whichCopy = request.POST['instanceId']
        instance = MusicInstance.objects.get(id = whichCopy)
        instance.status = 'a'
        instance.due_back = None
        instance.borrower = None
        instance.save()
        reservation = MusicInstanceReservation.objects.get(musicInstance = instance, takenout = True, returned = False, cancelled=False)
        id = reservation.borrowedid
        reservation.returneddate = date.today()
        reservation.returned = True
        reservation.save()
        userid = reservation.userid_id
        user = User.objects.get(id = str(userid))
        email = user.email
        send_mail(
            'Music Returned',
            'Your reservation: ' + str(id) +' has been returned',
            'adam@Bilkus.com',
            [email])
        messages.info(self.request, "Return Successful: %s has returned %s" % (user, whichCopy))
        return HttpResponseRedirect("/catalog")

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

def demo_piechart(request):
    """
    pieChart page
    """
    xdata = ["Apple", "Apricot", "Avocado", "Banana", "Boysenberries", "Blueberries", "Dates", "Grapefruit", "Kiwi", "Lemon"]
    ydata = [52, 48, 160, 94, 75, 71, 490, 82, 46, 17]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chartdata = {'x': xdata, 'y1': ydata, 'extra1': extra_serie}
    charttype = "pieChart"

    data = {
        'charttype': charttype,
        'chartdata': chartdata,
    }
    return render(None, 'catalog/piechart.html', data)


class MusicFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    class Meta:
        model = Music
        fields = ['genre', 'language']


'''
