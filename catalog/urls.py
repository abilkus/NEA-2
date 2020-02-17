from django.urls import path
from catalog import views

# The home page is the only one available to non-logged in users
# It displays differently depending on whether you are logged in
urlpatterns = [
    path('',views.HomePageView.as_view(),name='index'),
]


# From now on you must be logged in
# These patterns correspond to the functions available to anyone whether or not a member
urlpatterns += [
    path('musicList/', views.MusicListView.as_view(), name='musics'),
    path('musicDetail/<int:pk>', views.MusicDetailView.as_view(), name='music-detail'),
    path('composerList/', views.ComposerListView.as_view(), name='composers'),
    path('composerDetail/<int:pk>',
         views.ComposerDetailView.as_view(), name='composer_detail'),
]

# These patterns implement functions only available to members who therefore have reservation rights 
urlpatterns += [
    # the button which actually makes a reservation
    path('reserveAction/', views.ReserveAction.as_view(), name='reserveAction'),
    # list of music which has been borrowed or reserved by the user
    path('borrowedOrReservedByUser/', views.BorrowedOrReservedByUser.as_view(), name='my-borrowed'),
    path('cancelReserveAction/',views.CancelReserveAction.as_view(),name='cancelReserveAction'),
]

# These are only available to librarians
urlpatterns += [
    path('borrowAction/', views.borrowInstanceAction.as_view(), name='borrowAction'),
    path('renewAction/', views.renewInstanceAction.as_view(), name='renewAction'),
    path('returnAction/', views.returnInstanceAction.as_view(), name='returnAction'),
    path('borrowedOrReservedByAll/', views.BorrowedOrReservedByAll.as_view(), name='all-borrowed'),
    path('activityChart/', views.ActivityChart.as_view(), name='activityChart'),
]
'''
# Add URLConf to create, update, and delete composers
urlpatterns += [
    path('composer/create/', views.ComposerCreate.as_view(), name='composer_create'),
    path('composer/<int:pk>/update/', views.ComposerUpdate.as_view(), name='composer_update'),
    path('composer/<int:pk>/delete/', views.ComposerDelete.as_view(), name='composer_delete'),
]

# Add URLConf to create, update, and delete music
urlpatterns += [
    path('music/create/', views.MusicCreate.as_view(), name='music_create'),
    path('music/<int:pk>/update/', views.MusicUpdate.as_view(), name='music_update'),
    path('music/<int:pk>/delete/', views.MusicDelete.as_view(), name='music_delete'),
]
'''
