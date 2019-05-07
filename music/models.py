from django.db import models
from django.contrib.auth.models import Permission, User


class Album(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    artist = models.CharField(max_length = 100)
    album_title = models.CharField(max_length = 250)
    genre = models.CharField(max_length = 50)
    album_logo = models.FileField()
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.album_title + ' - ' + self.artist


class Song(models.Model):
    album = models.ForeignKey(Album, on_delete = models.CASCADE)
    song_title = models.CharField(max_length = 250)
    audio_file = models.FileField()
    is_favorite = models.BooleanField(default=False)

    def __str__(self):  
        return self.song_title