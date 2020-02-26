from django.db import models
from django.core.mail import send_mail
from django.utils.timezone import now
# Create your models here.
from django.utils import timezone
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.contrib.auth.models import User
import django_filters
from django.utils.crypto import get_random_string
import uuid  # Required for unique music instances
from datetime import date,timedelta

daysToReserve = 14
daysToBorrow = 122

class Genre(models.Model):
    """Model representing a musical genre (e.g. Jazz, Classical, Pop)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a musical genre (e.g. Jazz, Classical, Pop)"
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

class Music(models.Model):
    atomic = False
    """Model representing a piece of music  (but not a specific copy of that music)."""
    title = models.CharField(max_length=200)
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, null=True)
    # Foreign Key used because music can only have one composer but composers can have multiple sets of music
    # Composer as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    barcode = models.CharField('barcode', max_length=13,
                            help_text='the library unique reference code for this  piece')
    genre = models.ForeignKey(Genre,on_delete=models.SET_NULL, null=True)
    # ManyToManyField used because a genre can contain many sets of music and a Music can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('music-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title
    class Meta:
        permissions = (
            ("can_browse_catalog", "Can see what the music library has to offer"),
            ("can_see_availability", "Can see whether a piece is available"),
            ("can_self_reserve", "Can make a reservation for themself"),
            ("can_any_reserve", "Can make reservations on behalf of other users"),
            ("can_issue", "Can set reservation as borrowed"),
            ("can_return", "Can mark borrowed music as now returned"),
            ("can_see_reservation_detail", "Can see who has reserved or borrowed an instance"),
            ("has_all_permissions", "Can see admin pages"), 
        )



from django.contrib.auth.models import User  # Required to assign User as a borrower


class MusicInstance(models.Model):
    atomic = False
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    music = models.ForeignKey(Music, on_delete=models.SET_NULL, null=True)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def reserve(self,user,**kwargs):
        instance = self
        now = kwargs.get('dateOverride') # to use when creating test data
        if now == None:
            now = timezone.now()
        print("Making a reservation as at: %s" % (str(now)))
        reservationnumber = get_random_string(length=6, allowed_chars='1234567890')
        reservationnumber = int(reservationnumber)
        instance.status = 'r'
        instance.due_back = now + timedelta(days=daysToReserve)
        instance.borrower = user
        instance.save()
        
        reservation = MusicInstanceReservation(borrowedid = reservationnumber, musicInstance=instance , duedate = instance.due_back, takenoutdate = now, userid=user)
        activity = ActivityLog(activityCode = 'res', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=user)
        activity.save()
        reservation.save()
        return reservationnumber,instance

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
        return '{0} ({1} {2})'.format(self.id, self.music.title, self.music.composer.last_name)

class MusicInstanceReservation(models.Model):
    borrowedid = models.IntegerField()
    musicInstance = models.ForeignKey(MusicInstance, on_delete=models.SET_NULL, null=True)
    userid= models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    takenoutdate=models.DateTimeField(null=True,blank=True)
    returneddate=models.DateTimeField(null=True,blank=True)
    duedate = models.DateTimeField(null=True,blank=True)
    returned = models.BooleanField(default=False)
    takenout = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    def save(self,*args,**kwargs):
        if self.duedate == None:
            self.duedate = timezone.now + timedelta(days=daysToReserve)
        if self.takenoutdate == None:
            self.takenoutdate = timezone.now()
        return super(MusicInstanceReservation,self).save(*args,**kwargs)
    def cancel(self,user,**kwargs):
        instance = self.musicInstance
        instance.status = 'a'
        instance.due_back = None
        instance.borrower = None
        instance.save()
        reservation = self
        reservation.cancelled = True
        reservation.save()
        activity = ActivityLog(activityCode = 'can', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=user)
        activity.save()

    def borrow(self,user,**kwargs):
        reservation = self
        instance = self.musicInstance
        instance.status = 'o'
        instance.due_back = date.today() + timedelta(days = daysToBorrow)
        instance.save()
        
        reservation.due_back = instance.due_back
        reservation.takenout = True
        reservation.takenoutdate = date.today()
        reservation.returned = False
        reservation.save()
        activity = ActivityLog(activityCode = 'bor', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=user)
        activity.save()
        return instance
    def renew(self,user,**kwargs):
        reservation = self
        instance = self.musicInstance
        instance.due_back = date.today() + timedelta(days = daysToBorrow)
        instance.save()
        activity = ActivityLog(activityCode = 'ren', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=user)
        activity.save()
        reservation.duedate = instance.due_back
    def returns(self,user,**kwargs):
        reservation = self
        instance = self.musicInstance
        instance.status = 'a'
        instance.due_back = None
        instance.borrower = None
        instance.save()
        reservation.returned = True
        reservation.returneddate = date.today()
        reservation.save()
        activity = ActivityLog(activityCode = 'ret', music=instance.music,musicInstance=instance,composer=instance.music.composer,user=user)
        activity.save()
        return reservation.userid
    def hasExpired(self):
        return not self.takenout and not self.returned and not self.cancelled and (self.duedate < timezone.now()) 
    @staticmethod
    def cancelExpiredReservations(user):
        for res in MusicInstanceReservation.objects.all():
            if res.hasExpired():
                print("Cancelling an expired reservation")
                res.cancel(user)


ACTIVITY_CODE = (
        ('res', 'Reserve'),
        ('bor', 'Borrow'),
        ('can', 'Cancel Res'),
        ('ret', 'Return'),
        ('ren', 'Renew'),
    )
    

class ActivityLog(models.Model):
    activityTimestamp = models.DateTimeField(default=timezone.now)
    activityCode =  models.CharField(
        max_length=4,
        choices=ACTIVITY_CODE,
        null=False,
        help_text='The activity being logged')
    music = models.ForeignKey(Music, on_delete=models.SET_NULL, null=True)
    musicInstance = models.ForeignKey(MusicInstance, on_delete=models.SET_NULL, null=True)
    musicInstanceReservation = models.ForeignKey(MusicInstanceReservation, on_delete=models.SET_NULL, null=True)
    composer = models.ForeignKey(Composer, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
class Review(models.Model):
    music = models.ForeignKey(Music, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField()
    reviewDate = models.DateTimeField(default=timezone.now)

    @staticmethod
    def suggestionsForUser(user):
        latestGoodReviews = Review.objects.filter(user=user).filter(rating__gte=6).order_by('-reviewDate')
        for review in latestGoodReviews:
            print( "user %s rating %d and music %d" % (review.user.username,review.rating, review.music.id))
        numberOfGoodReviews = latestGoodReviews.count()
        if numberOfGoodReviews == 0:
            return []
        numberOfCandidates = 0
        compatibleUsers = set()
        for goodReview in latestGoodReviews:
            otherReviews = Review.objects.filter(music = goodReview.music).filter(rating__gte=goodReview.rating - 1).filter(rating__lte = goodReview.rating + 1)
            for otherReview in otherReviews:
                if otherReview.user == user:
                    continue
                compatibleUsers.add(otherReview.user.id)
                print(otherReview.user.id)
                print(otherReview.music.id)
        itemDict = {}
        for user in compatibleUsers:
            positiveReviews = Review.objects.filter(user=user).filter(rating__gte = 7)
            for positiveReview in positiveReviews:
                if MusicInstanceReservation.objects.filter(musicInstance__music=positiveReview.music,userid=user).exists():
                    continue
                currentVal = itemDict.get(positiveReview.music.id)
                if (currentVal == None):
                    currentVal = 1
                else:
                    currentVal = currentVal + 1
            itemDict[positiveReview.music] = currentVal
        nSuggestions = 0
        suggestions = []
        for k, v in sorted(itemDict.items(), key=lambda item: item[1],reverse = True):
            nSuggestions += 1
            if (nSuggestions > 4):
                break
            suggestions.append(k)
        return suggestions

