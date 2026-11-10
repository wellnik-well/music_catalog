from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PlaylistForm, TrackForm
from .models import Album, Artist, Genre, Playlist, PlaylistTrack, Track


# ---------- Треки ----------

def track_list(request):
    tracks = Track.objects.select_related("album__artist").prefetch_related("album__genres")
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "")
    year = request.GET.get("year", "").strip()

    if q:
        tracks = tracks.filter(
            Q(title__icontains=q) | Q(album__artist__name__icontains=q) | Q(album__title__icontains=q)
        )
    if genre.isdigit():
        tracks = tracks.filter(album__genres__id=int(genre))
    if year.isdigit():
        tracks = tracks.filter(album__year=int(year))

    tracks = tracks.distinct()
    page = Paginator(tracks, 20).get_page(request.GET.get("page"))
    return render(request, "catalog/track_list.html", {
        "section": "tracks",
        "page": page,
        "q": q,
        "genre": genre,
        "year": year,
        "genres": Genre.objects.all(),
        "playlists": Playlist.objects.all(),
    })


def track_create(request):
    form = TrackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Трек добавлен.")
        return redirect("track_list")
    return render(request, "catalog/track_form.html", {"section": "tracks", "form": form, "title": "Новый трек"})


def track_update(request, pk):
    track = get_object_or_404(Track, pk=pk)
    form = TrackForm(request.POST or None, instance=track)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("track_list")
    return render(request, "catalog/track_form.html", {"section": "tracks", "form": form, "title": "Редактирование трека"})


def track_delete(request, pk):
    track = get_object_or_404(Track, pk=pk)
    if request.method == "POST":
        track.delete()
        messages.success(request, "Трек удалён.")
        return redirect("track_list")
    return render(request, "catalog/track_confirm_delete.html", {"section": "tracks", "track": track})


# ---------- Исполнители и альбомы ----------

def artist_list(request):
    return render(request, "catalog/artist_list.html", {
        "section": "artists",
        "artists": Artist.objects.all(),
    })


def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    return render(request, "catalog/artist_detail.html", {
        "section": "artists",
        "artist": artist,
        "albums": artist.albums.prefetch_related("genres"),
    })


def album_list(request):
    return render(request, "catalog/album_list.html", {
        "section": "albums",
        "albums": Album.objects.select_related("artist").prefetch_related("genres"),
    })


def album_detail(request, pk):
    album = get_object_or_404(Album.objects.select_related("artist"), pk=pk)
    return render(request, "catalog/album_detail.html", {
        "section": "albums",
        "album": album,
        "tracks": album.tracks.all(),
    })


# ---------- Плейлисты ----------

def playlist_detail(request, pk=None):
    playlists = Playlist.objects.all()
    current = get_object_or_404(Playlist, pk=pk) if pk else playlists.first()
    entries = current.entries.select_related("track__album__artist") if current else []
    return render(request, "catalog/playlist_detail.html", {
        "section": "playlists",
        "playlists": playlists,
        "current": current,
        "entries": entries,
        "form": PlaylistForm(),
    })


@require_POST
def playlist_create(request):
    form = PlaylistForm(request.POST)
    if form.is_valid():
        playlist = form.save()
        messages.success(request, "Плейлист создан.")
        return redirect("playlist_detail", pk=playlist.pk)
    messages.error(request, "Введите название плейлиста, оно должно быть уникальным.")
    return redirect("playlist_list")


@require_POST
def playlist_delete(request, pk):
    get_object_or_404(Playlist, pk=pk).delete()
    messages.success(request, "Плейлист удалён.")
    return redirect("playlist_list")


@require_POST
def playlist_add_track(request):
    playlist = get_object_or_404(Playlist, pk=request.POST.get("playlist_id"))
    track = get_object_or_404(Track, pk=request.POST.get("track_id"))
    if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
        messages.info(request, f"«{track.title}» уже есть в плейлисте «{playlist.name}».")
    else:
        last = playlist.entries.aggregate(m=Max("position"))["m"] or 0
        PlaylistTrack.objects.create(playlist=playlist, track=track, position=last + 1)
        messages.success(request, f"«{track.title}» добавлен в «{playlist.name}».")
    return redirect("track_list")


@require_POST
def playlist_remove_entry(request, pk):
    entry = get_object_or_404(PlaylistTrack, pk=pk)
    playlist_pk = entry.playlist_id
    entry.delete()
    return redirect("playlist_detail", pk=playlist_pk)


@require_POST
def playlist_move_entry(request, pk, direction):
    entry = get_object_or_404(PlaylistTrack, pk=pk)
    siblings = PlaylistTrack.objects.filter(playlist=entry.playlist)
    if direction == "up":
        neighbor = siblings.filter(position__lt=entry.position).order_by("-position").first()
    else:
        neighbor = siblings.filter(position__gt=entry.position).order_by("position").first()
    if neighbor:
        with transaction.atomic():
            entry.position, neighbor.position = neighbor.position, entry.position
            entry.save(update_fields=["position"])
            neighbor.save(update_fields=["position"])
    return redirect("playlist_detail", pk=entry.playlist_id)
