from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin,ExportActionMixin,ImportExportMixin
from django.contrib.auth.models import User
from catalog.models import Composer, Genre, Music, MusicInstance, Language, MusicInstanceReservation,ActivityLog,Review


admin.site.register(Genre)
admin.site.register(Language)


class MusicInline(admin.TabularInline):
    """Defines format of inline music insertion (used in composerAdmin)"""
    model = Music


@admin.register(Composer)
class ComposerAdmin(ImportExportMixin,admin.ModelAdmin):
    """Administration object for Composer models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of music in composor view (inlines)
    """
    list_display = ('last_name',
                    'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [MusicInline]
    from_encoding = 'utf-8'


class MusicsInstanceInline(admin.TabularInline):
    """Defines format of inline instance insertion (used in ComposerAdmin)"""
    model = MusicInstance


class MusicAdmin(ImportExportMixin,admin.ModelAdmin):
    """Administration object for Music models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of music instances in music view (inlines)
    """
    list_display = ('title', 'composer', 'genre')
    inlines = [MusicsInstanceInline]


admin.site.register(Music, MusicAdmin)


@admin.register(MusicInstance)
class MusicInstanceAdmin(admin.ModelAdmin):
    """Administration object for musicInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('music', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

@admin.register(MusicInstanceReservation)
class MusicInstanceReservationAdmin(admin.ModelAdmin):
    model = MusicInstanceReservation

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    model = ActivityLog


@admin.register(Review)
class ReviewAdmin(ImportExportMixin,admin.ModelAdmin):
    model = Review;


from django.contrib import admin
from import_export import resources
from catalog.models import Composer

class ComposerResource(resources.ModelResource):

    class Meta:
        model = Composer

class MusicResource(resources.ModelResource):

    class Meta:
        model = Music

class GenreResource(resources.ModelResource):

    class Meta:
        model = Genre

admin.site.unregister(User)
class UserResource(resources.ModelResource):
    class Meta:
        model = User

class UserAdmin(ImportExportMixin,admin.ModelAdmin):
    """Administration object 
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    pass
admin.site.register(User, UserAdmin)
