from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime  # for checking renewal date range.

from django import forms
from django.db import models
from catalog.models import Music, Composer, MusicInstance, Genre, MusicInstanceReservation,ActivityLog
from django.contrib.auth.models import User


class RenewMusicForm(forms.Form):
    """Form for a librarian to renew music."""
    renewal_date = forms.DateField(
            help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data


class ReviewMusicForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    rating  = forms.IntegerField()
    def clean_rating(self):
        r = self.cleaned_data['rating']
        if r < 0 or r > 10:
            raise forms.ValidationError("Rating must be between 0 and 10")
        return r

class GetUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())