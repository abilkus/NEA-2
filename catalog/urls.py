from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('musics/', views.MusicListView.as_view(), name='musics'),
    path('music/<int:pk>', views.MusicDetailView.as_view(), name='music-detail'),
    path('composers/', views.ComposerListView.as_view(), name='composers'),
    path('composer/<int:pk>',
         views.ComposerDetailView.as_view(), name='composer_detail'),
]


urlpatterns += [
    path('mymusicss/', views.LoanedMusicByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedMusicAllListView.as_view(), name='all-borrowed'),  # Added for challenge
    path('myreserveds/', views.ReservedMusicByUserListView.as_view(), name='my-reserved'),
    path(r'reserved/', views.ReservedMusicAllListView.as_view(), name='all-reserved'),
]


# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('music/<uuid:pk>/renew/', views.renew_music_librarian, name='renew-music-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('composer/create/', views.ComposerCreate.as_view(), name='composer_create'),
    path('composer/<int:pk>/update/', views.ComposerUpdate.as_view(), name='composer_update'),
    path('composer/<int:pk>/delete/', views.ComposerDelete.as_view(), name='composer_delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('music/create/', views.MusicCreate.as_view(), name='music_create'),
    path('music/<int:pk>/update/', views.MusicUpdate.as_view(), name='music_update'),
    path('music/<int:pk>/delete/', views.MusicDelete.as_view(), name='music_delete'),
]
