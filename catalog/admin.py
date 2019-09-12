from django.contrib import admin

# Register your models here.

from .models import Composer, Genre, Music, MusicInstance, Language


admin.site.register(Genre)
admin.site.register(Language)


class MusicInline(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""
    model = Music


@admin.register(Composer)
class ComposerAdmin(admin.ModelAdmin):
    """Administration object for Author models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of books in author view (inlines)
    """
    list_display = ('last_name',
                    'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [MusicInline]


class MusicsInstanceInline(admin.TabularInline):
    """Defines format of inline book instance insertion (used in BookAdmin)"""
    model = MusicInstance


class MusicAdmin(admin.ModelAdmin):
    """Administration object for Book models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of book instances in book view (inlines)
    """
    list_display = ('title', 'composer', 'display_genre')
    inlines = [MusicsInstanceInline]


admin.site.register(Music, MusicAdmin)


@admin.register(MusicInstance)
class MusicInstanceAdmin(admin.ModelAdmin):
    """Administration object for BookInstance models.
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
