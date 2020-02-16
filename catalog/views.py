from django.shortcuts import render
from django.views import View
# Create your views here.
from django.http import HttpResponse
from .models import Music, Composer, MusicInstance, Genre, MusicInstanceReservation
from django.template import loader
from django.utils.crypto import get_random_string
from datetime import date
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
import datetime
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
# Added as part of challenge!
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
import datetime
from catalog.forms import RenewMusicForm
import django_filters
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Composer
from django.shortcuts import render
import random
import datetime
import time
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group

def is_in_group(user,group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

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
        if self.request.user.has_perm('can_self_reserve'):
            can_reserve = True
        xxx = (
            {'can_reserve':can_reserve ,'num_music': num_music, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_composers': num_composers,
                 'num_visits': num_visits})
        context.update(xxx)
        return context

    def render_to_response(self,context,**kwargs):
        return super().render_to_response(context);

class MusicListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view for a list of music."""
    model = Music
    paginate_by = 10
    permission_required = "silly"
    def get_context_data(self, **kwargs):
        messages.info(self.request,"MUSIC LIST VIEW HERE")
        context = super().get_context_data(**kwargs)
        context['hackedby'] = "Gary"
        #raise PermissionDenied
        # self.use_template = "nonexistent.html"
        return context
        
    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('can_browse_catalog'):
           return False    
        return True       

class ReserveAction(PermissionRequiredMixin,View) :     
    def has_permission(self):
        if not self.request.user.is_authenticated:
           return False
        if not self.request.user.has_perm('can_self_reserve'):
            if not self.request.user.has_perm('can_any_reserve'):
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
        reservation = MusicInstanceReservation(borrowedid = reservationnumber, musicInstance=instance , takenoutdate = date.today(), userid=request.user, takenout= False)
        reservation.save()
        send_mail(
            'Music Reserved',
            'Your Borrowed id is: ' + str(reservationnumber),
            'adam@Bilkus.com',
            [emailAddress])
        return HttpResponse( ("You have reserved %s and your reservation number is %s") % (whichCopy, reservationnumber))



class MusicDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Music

class ComposerListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Composer
    paginate_by = 10
    permission_required = 'can_browse_catalog'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hackedby'] = "Adam"
        return context
    def has_permission(self):
        if not self.request.user.is_authenticated:
            return False
        if not self.request.user.has_perm('can_browse_catalog'):
            return False
        return True

class ComposerDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Composer





class BorrowedUser(LoginRequiredMixin, generic.ListView):
    model = Music
    template_name = 'catalog/music_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        is_borrowed = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='o').filter(borrower=self.request.user)
        return Music.objects.annotate(is_borrowed=Exists(is_borrowed)).filter(is_borrowed=True)

def BorrowedMusicDetail(request, pk):
    if request.user.is_authenticated:
        username = request.user
    template = loader.get_template("catalog/borrowed_music.html")
    music=Music.objects.get(pk=pk)
    reserved=music.musicinstance_set.filter(status__exact = 'o').filter(borrower=username)
    context= {"music":music,"available":reserved}
    return HttpResponse(template.render(context,request))

class ReservedUser(LoginRequiredMixin, generic.ListView):
    model = Music
    template_name = 'catalog/music_list_reserved_user.html'
    paginate_by = 10

    def get_queryset(self):
        is_borrowed = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='r').filter(borrower=self.request.user)
        return Music.objects.annotate(is_borrowed=Exists(is_borrowed)).filter(is_borrowed=True)


def ReservedMusicDetail(request, pk):
    if request.user.is_authenticated:
        username = request.user
    template = loader.get_template("catalog/reserved_music.html")
    music=Music.objects.get(pk=pk)
    reserved=music.musicinstance_set.filter(status__exact = 'r').filter(borrower=username)
    context= {"music":music,"available":reserved}
    return HttpResponse(template.render(context,request))



class LoanedMusicAllListView(generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = MusicInstance
    template_name = 'catalog/musicinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return MusicInstance.objects.filter(status__exact='o').order_by('due_back')

'''class ReservedMusicAllListView(PermissionRequiredMixin, generic.ListView):
    model = Music
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/musicinstance_list_reserved_all.html'
    paginate_by = 10

    def get_queryset(self):
        return MusicInstance.objects.filter(status__exact='r').order_by('due_back')
    





def renew_music_librarian(request, pk):
    """View function for renewing a specific musicInstance by librarian."""
    music_instance = get_object_or_404(MusicInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewMusicForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            music_instance.due_back = form.cleaned_data['renewal_date']
            music_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewMusicForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'music_instance': music_instance,
    }

    return render(request, 'catalog/music_renew_librarian.html', context)




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

# Classes created for the forms challenge
class MusicCreate(CreateView):
    model = Music
    fields = '__all__'

class MusicUpdate(UpdateView):
    model = Music
    fields = '__all__'

class MusicDelete(DeleteView):
    model = Music
    success_url = reverse_lazy('musics')

class Reserve(generic.ListView):
    model = Music
    template_name = 'catalog/music_list_available_all.html'
    paginate_by = 10

    def get_queryset(self):
        is_available = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='a')
        return Music.objects.annotate(is_available=Exists(is_available)).filter(is_available=True)

class Borrow(generic.ListView):
    model = Music
    template_name = 'catalog/music_list_reserved_all.html'
    paginate_by = 10

    def get_queryset(self):
        is_reserved = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='r')
        return Music.objects.annotate(is_reserved=Exists(is_reserved)).filter(is_reserved=True)
class Return(generic.ListView):
    model = Music
    template_name = 'catalog/music_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        is_borrowed = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='o')
        return Music.objects.annotate(is_borrowed=Exists(is_borrowed)).filter(is_borrowed=True)

def BorrowMusicDetail(request, pk):
    template = loader.get_template("catalog/borrow_music.html")
    music=Music.objects.get(pk=pk)
    reserved=music.musicinstance_set.filter(status__exact = 'r')
    context= {"music":music,"reserved":reserved}
    return HttpResponse(template.render(context,request))
def BorrowMusicDetailUser(request, pk):
    template = loader.get_template('catalog/reserved_music.html')
    music = Music.objects.get(pk = pk)
    if request.user.is_authenticated:
        username = request.user
    reserved = music.musicinstance_set.filter(status__exact = 'r', borrower_id = username.id)
    context = {"music":music, "reserved":reserved, "user":username}
    return HttpResponse(template.render(context,request))
def ReturnMusicDetail(request, pk):
    template = loader.get_template("catalog/return_music.html")
    music=Music.objects.get(pk=pk)
    borrowed=music.musicinstance_set.filter(status__exact = 'o')
    context= {"music":music,"available":borrowed}
    return HttpResponse(template.render(context,request))
def ReserveMusicDetail(request, pk):
    template = loader.get_template("catalog/reserve_music.html")
    music=Music.objects.get(pk=pk)
    available=music.musicinstance_set.filter(status__exact = 'a')
    context= {"music":music,"available":available}
    return HttpResponse(template.render(context,request))


def BorrowAction(request):
    whichCopy= request.POST['borrowbutton']
    a = MusicInstance.objects.get(id = whichCopy)
    a.status = 'o'
    a.due_back = date.today() + timedelta(days=42)
    a.save()
    p = MusicInstanceReservation.objects.get(musicInstance = a, takenout = False)
    p.due_back = a.due_back
    p.takenout = True
    p.takenoutdate=date.today()
    p.returned=False
    p.save()
    userid = p.userid_id
    user = User.objects.get(id=str(userid))
    username=user.username
    reservationnumber = p.borrowedid
    email = user.email
    send_mail(
        'Music Borrowed',
        'Your Borrowed id is: ' + str(reservationnumber),
        'adam@Bilkus.com',
        [email])

    return HttpResponse( ("%s has borrowed %s") % (username, whichCopy))

def bview(request):
    return HttpResponse("Hello World")

def ReturnAction(request):
    whichCopy= request.POST['returnbutton']
    a = MusicInstance.objects.get(id = whichCopy)
    a.status = 'a'
    a.due_back = None
    a.borrower = None
    a.save()
    p = MusicInstanceReservation.objects.get(musicInstance = a, takenout=True, returned= False)
    c=p.borrowedid
    p.returneddate= date.today()
    p.returned = True
    p.save()
    d = p.userid_id
    e = User.objects.get(id = str(d))
    f = e.email
    send_mail(
        'Music Returned',
        'Your reservation: ' + str(c) +' has been returned',
        'adam@Bilkus.com',
        [f])
    return HttpResponse( ("You have returned %s ") % (whichCopy))

def map(request):
    template = loader.get_template("catalog/maps.html")
    return HttpResponse(template.render())



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
