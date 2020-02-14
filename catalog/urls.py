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
    path('mymusicss/', views.BorrowedUser.as_view(), name='my-borrowed'),
    path('reservedMusicDetailUser/<int:pk>', views.BorrowMusicDetail, name='reserved-music'),
    path('borrowedMusicDetailUser/<int:pk>', views.BorrowedMusicDetail, name = 'borrowed-music'),
    path('borrowed/', views.Return.as_view(), name='return'),  # Added for challenge
    path('returnAction',views.ReturnAction, name='return_action'),
    path('borrowedMusicDetail/<int:pk>', views.ReturnMusicDetail, name='return-music'),
    path('myreserveds/', views.ReservedUser.as_view(), name='my-reserved'),
    path('reserved/', views.Borrow.as_view(), name='borrow'),
    path('reservedMusicDetailAll/<int:pk>', views.BorrowMusicDetail,name='borrow-music'),
    path('borrowAction',views.BorrowAction,name='borrow_action'),
    path('map', views.map, name='mapping'),
    path('piechart', views.demo_piechart, name='chart')

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
urlpatterns += [ 

    path('reserve/',views.Reserve.as_view(),name='reserve'),
    path('reserveMusicDetail/<int:pk>', views.ReserveMusicDetail,name='reserve-music'),
    path('reserveAction',views.ReserveAction,name='reserve_action')
    ]

