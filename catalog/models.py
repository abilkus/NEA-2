from django.db import models
from django.core.mail import send_mail
from django.utils.timezone import now
# Create your models here.
from django.utils import timezone
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.contrib.auth.models import User

class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
        )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the music's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Music(models.Model):
    atomic = False
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    composer = models.ForeignKey('Composer', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because music can only have one composer but composers can have multiple sets of music
    # Composer as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this music")
    # ManyToManyField used because a genre can contain many sets of music and a Music can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('music-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


import uuid  # Required for unique music instances
from datetime import date

from django.contrib.auth.models import User  # Required to assign User as a borrower


class MusicInstance(models.Model):
    atomic = False
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    music = models.ForeignKey('music', on_delete=models.SET_NULL, null=True)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            send_mail(
                'Music overdue',
                'Your Music is overdue',
                'adam@Bilkus.com',
                ['adam@Bilkus.com'],
                fail_silently = False,
            )
    
            print("hELLO")
            return True
        
        return False
    
    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        help_text='Music availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.id, self.music.title)


class Composer(models.Model):
    atomic = False
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('composer_detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.last_name, self.first_name)

class MusicInstanceReservation(models.Model):
    borrowedid = models.IntegerField()
    musicInstance = models.ForeignKey("musicInstance", on_delete=models.SET_NULL, null=True)
    userid= models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    takenoutdate=models.DateTimeField(default=timezone.now)
    returneddate=models.DateTimeField(default=timezone.now)
    returned = models.CharField(max_length=5, blank=True)
    takenout = models.CharField(max_length=5, blank = True)
    duedate = models.DateTimeField(default=timezone.now)
