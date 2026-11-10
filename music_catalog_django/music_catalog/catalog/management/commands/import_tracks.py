import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Album, Artist, Genre, Track, parse_duration

REQUIRED = {"artist", "album", "title", "duration"}


class Command(BaseCommand):
    help = (
        "Импорт треков из CSV. Обязательные столбцы: artist, album, title, duration (мм:сс). "
        "Необязательные: year, track_number, genre (несколько жанров через «;»)."
    )

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Путь к CSV-файлу в кодировке UTF-8")

    def handle(self, *args, **options):
        added, updated, rejected = 0, 0, []

        try:
            with open(options["csv_path"], encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                missing = REQUIRED - set(reader.fieldnames or [])
                if missing:
                    raise CommandError(f"В файле не хватает столбцов: {', '.join(sorted(missing))}")
                rows = list(enumerate(reader, start=2))
        except FileNotFoundError:
            raise CommandError("Файл не найден.")

        for line_no, row in rows:
            try:
                with transaction.atomic():
                    artist, _ = Artist.objects.get_or_create(name=row["artist"].strip())
                    year = int(row["year"]) if row.get("year") else None
                    album, _ = Album.objects.get_or_create(
                        artist=artist, title=row["album"].strip(), defaults={"year": year}
                    )
                    for name in (row.get("genre") or "").split(";"):
                        if name.strip():
                            album.genres.add(Genre.objects.get_or_create(name=name.strip())[0])

                    track_number = int(row["track_number"]) if row.get("track_number") else None
                    _, created = Track.objects.update_or_create(
                        album=album,
                        title=row["title"].strip(),
                        defaults={
                            "track_number": track_number,
                            "duration_seconds": parse_duration(row["duration"]),
                        },
                    )
                    if created:
                        added += 1
                    else:
                        updated += 1
            except (ValueError, KeyError) as exc:
                rejected.append(f"строка {line_no}: {exc}")

        self.stdout.write(self.style.SUCCESS(f"Добавлено: {added}, обновлено: {updated}"))
        for message in rejected:
            self.stdout.write(self.style.WARNING(f"Отклонено — {message}"))
        if rejected:
            self.stdout.write(f"Отклонено строк: {len(rejected)}")
