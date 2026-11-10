from django.contrib import admin

from .models import Album, Artist, Genre, Playlist, PlaylistTrack, Track


class TrackInline(admin.TabularInline):
    model = Track
    extra = 1


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "year")
    list_filter = ("genres", "year")
    search_fields = ("title", "artist__name")
    inlines = [TrackInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 0


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    inlines = [PlaylistTrackInline]
