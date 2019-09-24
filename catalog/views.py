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


class LoanedMusicByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = MusicInstance
    template_name = 'catalog/musicinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return MusicInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class ReservedMusicByUserListView(LoginRequiredMixin, generic.ListView):
    model = MusicInstance
    template_name = 'catalog/musicinstance_list_reserved_user.html'
    paginate_by = 10

    def get_queryset(self):
        return MusicInstance.objects.filter(borrower=self.request.user).filter(status__exact='r').order_by('due_back')

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

class ReservedMusicAllListView(PermissionRequiredMixin, generic.ListView):
    model = Music
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/musicinstance_list_reserved_all.html'
    paginate_by = 10

    def get_queryset(self):
        return MusicInstance.objects.filter(status__exact='r').order_by('due_back')
    

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

class Borrow(generic.ListView):
    model = Music
    template_name = 'catalog/music_list_available_all.html'
    paginate_by = 10

    def get_queryset(self):
        is_available = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='a')
        return Music.objects.annotate(is_available=Exists(is_available)).filter(is_available=True)

def BorrowMusicDetail(request, pk):
    template = loader.get_template("catalog/reserve_music.html")
    music=Music.objects.get(pk=pk)
    available=music.musicinstance_set.filter(status__exact = 'a')
    context= {"music":music,"available":available}
    return HttpResponse(template.render(context,request))
from django.contrib.auth import get_user_model
def BorrowAction(request):
    whichCopy= request.POST['reservebutton']
    reservationnumber = get_random_string(length=6, allowed_chars='1234567890')
    reservationnumber = int(reservationnumber)
    if request.user.is_authenticated:
        username = request.user
    a = MusicInstance.objects.get(id = whichCopy)
    a.status = 'r'
    a.due_back = datetime.date.today() + timedelta(days=7)
    a.borrower = username
    a.save()
    b=request.user
    c= b.email
    print(c)
    p = MusicInstanceReservation(borrowedid = reservationnumber, musicInstance=a , takenoutdate = date.today(), userid=username)
    p.save()
    send_mail(
        'Music Reserved',
        'Your reservation id is: ' + str(reservationnumber),
        'adam@Bilkus.com',
        [c])
    return HttpResponse( ("You have reserved %s and your reservation number is %s") % (whichCopy, reservationnumber))

class ChangeToBorrowed(generic.ListView):
    model = Music
    template_name = 'catalog/musicinstance_list_reserved_all.html'
    paginate_by=10
    def get_queryset(self):
        is_reserved = MusicInstance.objects.filter(music=OuterRef('pk'),status__exact='r')
        return Music.objects.annotate(is_available=Exists(is_reserved)).filter(is_reserved=True)
