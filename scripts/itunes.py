import sys
import itertools
import os.path
from pathlib import Path
from datetime import datetime

from ScriptingBridge import SBApplication
from Foundation import NSMutableIndexSet, NSURL


class ITunes(object):
    def __init__(self):
        self.app = app = SBApplication.applicationWithBundleIdentifier_(
            'com.apple.iTunes')
        self.app.setFixedIndexing_(True)
        self.source = first(app.sources(), lambda x: x.name() == 'Library')

    @property
    def playlists(self):
        return (Playlist(p) for p in self.source.userPlaylists())

    @property
    def tracks(self):
        "Return all music tracks."
        return self['Music'].tracks

    def add_playlist(self, name):
        props = dict(name=name)
        playlist = self.app.classForScriptingClass_("playlist").alloc().initWithProperties_(props)
        self.app.sources()[0].playlists().insertObject_atIndex_(playlist, 0)
        return Playlist(playlist)

    def __getitem__(self, name):
        playlist = first(self.source.userPlaylists(), lambda x: x.name() == name)
        return Playlist(playlist)


class Playlist(object):
    "Wrapper class for ITunesUserPlaylist"
    def __init__(self, playlist):
        self._playlist = playlist

    @property
    def name(self):
        return self._playlist.name()

    @property
    def tracks(self):
        return (Track(t) for t in self._playlist.tracks())

    def add_track(self, track):
        track._track.duplicateTo_(self._playlist)


class Track(object):
    "Wrapper class for ITunesTrack"
    def __init__(self, track):
        self._track = track

    @property
    def unique_id(self): return self._track.id()

    @property
    def title(self): return self._track.name()

    @property
    def artist(self): return self._track.artist()

    @property
    def rating(self): return self._track.rating()

    @property
    def genre(self): return self._track.genre()

    @property
    def date_added(self):
        return self._track

    @property
    def stars(self):
        rating = self.rating
        if rating == 100:
            return 5
        elif rating >= 80:
            return 4
        elif rating >= 60:
            return 3
        elif rating >= 40:
            return 2
        elif rating >= 20:
            return 1
        else:
            return 0

    @property
    def path(self):
        return Path(self._track.get().location().path())

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def lyrics(self):
        return self._track.lyrics()

    @property
    def duration(self):
        return self._track.duration()

    @property
    def date_added(self):
        return self._track.dateAdded().timeIntervalSince1970()


def first(iterable, predicate):
    "Return the first element in `iterable` that matches `predicate`."
    try:
        return next(filter(predicate, iterable))
    except StopIteration:
        return None
