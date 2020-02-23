from django.urls import path
from catalog import views

# The home page is the only one available to non-logged in users
# It displays differently depending on whether you are logged in
urlpatterns = [
    path('',views.HomePageView.as_view(),name='index'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),

]


# From now on you must be logged in
# These patterns correspond to the functions available to anyone whether or not a member
urlpatterns += [
    path('musicListOld/', views.MusicListView.as_view(), name='musics'),
    path('musicList/', views.MusicListGridView.as_view(), name='musicgrid'),
    path('musicDetail/<int:pk>', views.MusicDetailView.as_view(), name='music-detail'),
    path('composerList/', views.ComposerListView.as_view(), name='composers'),
    path('composerDetail/<int:pk>',
         views.ComposerDetailView.as_view(), name='composer_detail'),
]

# These patterns implement functions only available to members who therefore have reservation rights 
urlpatterns += [
    path('suggestions/<int:pk>', views.SuggestionsView.as_view(), name='suggestions'),
    # the button which actually makes a reservation
    path('reserveAction/', views.ReserveAction.as_view(), name='reserveAction'),
    # list of music which has been borrowed or reserved by the user
    path('borrowedOrReservedByUser/', views.BorrowedOrReservedByUser.as_view(), name='my-borrowed'),
    path('cancelReserveAction/',views.CancelReserveAction.as_view(),name='cancelReserveAction'),
]

# These are only available to librarians
urlpatterns += [
    path('borrowAction/', views.BorrowInstanceAction.as_view(), name='borrowAction'),
    path('renewAction/', views.RenewInstanceAction.as_view(), name='renewAction'),
    path('returnAction/', views.ReturnInstanceAction.as_view(), name='returnAction'),
    path('reviewMusic/<int:pk>', views.ReviewMusic.as_view(), name='reviewMusic'),

    path('borrowedOrReservedByAll/', views.BorrowedOrReservedByAll.as_view(), name='all-borrowed'),
    path('borrowedPie/', views.BorrowedPie.as_view(), name='borrowedPie'),
    path('borrowedList/', views.BorrowedList.as_view(), name='borrowedList'),
    path('routineMaintenance/',views.RoutineMaintenance.as_view(),name='routineMaintenance'),
    path('createRandomMusic/',views.CreateRandomMusic.as_view(),name='createRandomMusic'),
    path('createRandomMusicInstances/',views.CreateRandomMusicInstances.as_view(),name='createRandomMusicInstances'),
    path('createRandomReviews/',views.CreateRandomReviews.as_view(),name='createRandomReviews'),
    path('createRandomGenre/',views.CreateRandomGenre.as_view(),name='createRandomGenre'),
    path('assignRandomGenre/',views.AssignRandomGenre.as_view(),name='assignRandomGenre'),
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
