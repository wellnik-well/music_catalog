import re

from django.core.validators import MinValueValidator
from django.db import models


def parse_duration(value):
    """Переводит строку «мм:сс» в количество секунд. Бросает ValueError при ошибке."""
    match = re.fullmatch(r"(-?)(\d+):(\d{2})", value.strip())
    if not match:
        raise ValueError("введите время в формате мм:сс")
    if match.group(1):
        raise ValueError("длительность не может быть отрицательной")
    minutes, seconds = int(match.group(2)), int(match.group(3))
    if seconds > 59:
        raise ValueError("секунды должны быть от 00 до 59")
    return minutes * 60 + seconds


class Genre(models.Model):
    name = models.CharField("Жанр", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "жанр"
        verbose_name_plural = "жанры"

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField("Имя", max_length=200, unique=True)
    country = models.CharField("Страна", max_length=100, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "исполнитель"
        verbose_name_plural = "исполнители"

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField("Название", max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums", verbose_name="Исполнитель")
    year = models.PositiveSmallIntegerField("Год выпуска", null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="albums", verbose_name="Жанры")

    class Meta:
        ordering = ["artist__name", "year", "title"]
        verbose_name = "альбом"
        verbose_name_plural = "альбомы"

    def __str__(self):
        return f"{self.artist} — {self.title}"

    @property
    def genre_names(self):
        return ", ".join(g.name for g in self.genres.all())


class Track(models.Model):
    title = models.CharField("Название", max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks", verbose_name="Альбом")
    track_number = models.PositiveSmallIntegerField("Номер в альбоме", null=True, blank=True)
    duration_seconds = models.PositiveIntegerField("Длительность, сек", validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["album__artist__name", "album__year", "track_number", "title"]
        verbose_name = "трек"
        verbose_name_plural = "треки"

    def __str__(self):
        return self.title

    @property
    def artist(self):
        return self.album.artist

    @property
    def duration_display(self):
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes}:{seconds:02d}"


class Playlist(models.Model):
    name = models.CharField("Название", max_length=150, unique=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "плейлист"
        verbose_name_plural = "плейлисты"

    def __str__(self):
        return self.name


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="entries")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="playlist_entries")
    position = models.PositiveIntegerField("Порядковый номер")

    class Meta:
        ordering = ["position"]
        unique_together = [("playlist", "track")]
        verbose_name = "трек в плейлисте"
        verbose_name_plural = "треки в плейлистах"

    def __str__(self):
        return f"{self.playlist}: {self.track}"
