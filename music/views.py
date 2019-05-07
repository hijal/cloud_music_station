from django.contrib.auth import authenticate, login 
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404,redirect
from.models import Album, Song
from .forms import AlbumForm, SongForm, UserForm
from django.http import Http404
from django.http import JsonResponse
from django.db.models import Q


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']



def create_album(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                c = {
                    'album': album,
                    'form': form,
                    'error_message': "Image file must be PNG, JPG , JPEG or gif"
                }
                return render(request, 'music/create_album.html', c)
            album.save()
            c = {
                'album': album
            }
            return render(request, 'music/detail.html', c)
        c = {
            'form': form
        }
        return render(request, 'music/create_album.html', c)


def create_song(request, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk = album_id)
    if form.is_valid():
        albums_songs = album.song_set.all()
        for song in albums_songs:
            clean = form.cleaned_data.get('song_title')
            if song.song_title == clean:
                c = {
                    'album': album,
                    'form': form,
                    'error_message': 'You added this song already!'
                }
                return render(request, 'music/create_song.html', c)
        song = form.save(commit=False)
        song.album = album
        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            c = {
                'album': album,
                'form': form,
                'error_message': 'You added this song already!'
            }
            return render(request, 'music/create_song.html', c)
        song.save()
        c = {
            'album': album
        }
        return render(request, 'music/detail.html', c)
    c = {
        'album': album,
        'form': form
    }
    return render(request, 'music/create_song.html', c)



def favorite(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        selected_song = album.song_set.get(pk=request.POST['song'])
    except(KeyError, Song.DoesNotExist):
        c = {
        'album': album,
        'error_message': "You didn't select any song!"
        }
        return render(request, 'music/detail.html', c)
    else:
        selected_song.is_favorite = True
        selected_song.save()
        c = {
        'album': album
        }
        return render(request, 'music/detail.html', c)

def dis_favorite(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        selected_song = album.song_set.get(pk=request.POST['song'])
    except(KeyError, Song.DoesNotExist):
        c = {
        'album': album,
        'error_message': "You didn't select any song!"
        }
        return render(request, 'music/detail.html', c)
    else:
        selected_song.is_favorite = False
        selected_song.save()
        c = {
        'album': album
        }
        return render(request, 'music/detail.html', c)

def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk = album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except(KeyError, Album.DoesNotExist):
        return JsonResponse({success: False})
    else:
        return JsonResponse({success: True})


def delete_album(request, album_id):
    album = Album.objects.get(pk = album_id)
    album.delete()
    albums = Album.objects.filter(user = request.user)
    c = {
        'albums': albums
    }
    return render(request, 'music/index.html', c)


def delete_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk = album_id)
    song = Song.objects.get(pk = song_id)
    song.delete()
    c = {
        'album': album
    }
    return render(request, 'music/detail.html', c)


def index(request):
    albums = Album.objects.all()
    c = {
        'albums': albums
    }
    return render(request, 'music/index.html', c)


def detail(request, album_id):
    album = get_object_or_404(Album, pk = album_id)
    c = {
        'album': album
    }
    return render(request, 'music/detail.html', c)



def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    c = {
        'form': form
    }
    return render(request, 'music/login.html', c)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user = request.user)
                c = {
                    'albums': albums
                }
                return render(request, 'music/index.html', c)
            else:
                c = {
                    'error_message': 'Your account has been disabled.'
                }
                return render(request, 'music/login.html', c)
        else:
            c = {
                'error_message': 'Invalid login'
            }
            return render(request, 'music/login.html', c)
    return render(request, 'music/login.html')            


def register(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user= request.user)
                c = {
                    'albums': albums
                }
                return render(request, 'music/index.html', c)
    c = {
        'form': form
    }
    return render(request, 'music/register.html', c)



def songs(request, filter_by):
    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            for album in Album.objects.filter(user = request.user):
                for song in album.song_set.all():
                    song_ids.append(song.pk)
            users_songs = Song.objects.filter(pk__in = song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite = True)
        except Album.DoesNotExist:
            users_songs = []
        c = {
            'song_list': users_songs,
            'filter_by': filter_by
        }
        return render(request, 'music/songs.html', c)


def album_list(request):
    albums = Album.objects.filter(user = request.user)
    c = {
        'albums': albums
    }
    return render(request, 'music/album_list.html', c)