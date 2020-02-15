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
import django_filters
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_music = Music.objects.all().count()
    num_instances = MusicInstance.objects.all().count()
    # Available copies of books
    num_instances_available = MusicInstance.objects.filter(status__exact='a').count()
    num_composers = Composer.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_music': num_music, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_composers': num_composers,
                 'num_visits': num_visits},
    )


from django.views import generic


class MusicListView(generic.ListView):
    """Generic class-based view for a list of music."""
    model = Music
    paginate_by = 10


class MusicDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Music


class ComposerListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Composer
    paginate_by = 10


class ComposerDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Composer


from django.contrib.auth.mixins import LoginRequiredMixin


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

# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedMusicAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = MusicInstance
    permission_required = 'catalog.can_mark_returned'
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
    
'''
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

# from .forms import RenewmusicForm
from catalog.forms import RenewMusicForm


@permission_required('catalog.can_mark_returned')
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


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Composer


class ComposerCreate(PermissionRequiredMixin, CreateView):
    model = Composer
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'


class ComposerUpdate(PermissionRequiredMixin, UpdateView):
    model = Composer
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class ComposerDelete(PermissionRequiredMixin, DeleteView):
    model = Composer
    success_url = reverse_lazy('composers')
    permission_required = 'catalog.can_mark_returned'


# Classes created for the forms challenge
class MusicCreate(PermissionRequiredMixin, CreateView):
    model = Music
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class MusicUpdate(PermissionRequiredMixin, UpdateView):
    model = Music
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class MusicDelete(PermissionRequiredMixin, DeleteView):
    model = Music
    success_url = reverse_lazy('musics')
    permission_required = 'catalog.can_mark_returned'

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
from django.contrib.auth import get_user_model
def ReserveAction(request):
    whichCopy= request.POST['reservebutton']
    reservationnumber = get_random_string(length=6, allowed_chars='1234567890')
    reservationnumber = int(reservationnumber)
    if request.user.is_authenticated:
        username = request.user
    a = MusicInstance.objects.get(id = whichCopy)
    a.status = 'r'
    a.due_back = datetime.date.today() + timedelta(days=122)
    a.borrower = username
    a.save()
    b=request.user
    c= b.email
    print(c)
    p = MusicInstanceReservation(borrowedid = reservationnumber, musicInstance=a , takenoutdate = date.today(), userid=username, takenout= False)
    p.save()
    send_mail(
        'Music Reserved',
        'Your Borrowed id is: ' + str(reservationnumber),
        'adam@Bilkus.com',
        [c])
    return HttpResponse( ("You have reserved %s and your reservation number is %s") % (whichCopy, reservationnumber))

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

from django.shortcuts import render
import random
import datetime
import time

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

