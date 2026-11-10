from django import forms
from django.core.exceptions import ValidationError

from .models import Playlist, Track, parse_duration


class TrackForm(forms.ModelForm):
    duration = forms.CharField(label="Длительность (мм:сс)", max_length=10, help_text="Например, 5:55")

    class Meta:
        model = Track
        fields = ["title", "album", "track_number"]
        labels = {"title": "Название", "album": "Альбом", "track_number": "Номер в альбоме"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["duration"] = self.instance.duration_display

    def clean_duration(self):
        try:
            return parse_duration(self.cleaned_data["duration"])
        except ValueError as exc:
            raise ValidationError(str(exc).capitalize())

    def save(self, commit=True):
        track = super().save(commit=False)
        track.duration_seconds = self.cleaned_data["duration"]
        if commit:
            track.save()
        return track


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["name"]
        labels = {"name": "Название плейлиста"}
