from django.urls import path

from . import views

urlpatterns = [
    path("", views.track_list, name="track_list"),
    path("tracks/new/", views.track_create, name="track_create"),
    path("tracks/<int:pk>/edit/", views.track_update, name="track_update"),
    path("tracks/<int:pk>/delete/", views.track_delete, name="track_delete"),

    path("artists/", views.artist_list, name="artist_list"),
    path("artists/<int:pk>/", views.artist_detail, name="artist_detail"),

    path("albums/", views.album_list, name="album_list"),
    path("albums/<int:pk>/", views.album_detail, name="album_detail"),

    path("playlists/", views.playlist_detail, name="playlist_list"),
    path("playlists/<int:pk>/", views.playlist_detail, name="playlist_detail"),
    path("playlists/create/", views.playlist_create, name="playlist_create"),
    path("playlists/<int:pk>/delete/", views.playlist_delete, name="playlist_delete"),
    path("playlists/add-track/", views.playlist_add_track, name="playlist_add_track"),
    path("playlists/entries/<int:pk>/remove/", views.playlist_remove_entry, name="playlist_remove_entry"),
    path("playlists/entries/<int:pk>/move/<str:direction>/", views.playlist_move_entry, name="playlist_move_entry"),
]
