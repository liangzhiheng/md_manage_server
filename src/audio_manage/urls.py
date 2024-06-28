from django.urls import path

from audio_manage.views.singer import SingerView, SingerDetailView, SingerAvatarView
from audio_manage.views.album import AlbumView, AlbumDetailView
from audio_manage.views.group import GroupView


urlpatterns = [
    path("singer", SingerView.as_view()),
    path("singer/<id>", SingerDetailView.as_view()),
    path("singer/avatar/<id>", SingerAvatarView.as_view()),
    path("album", AlbumView.as_view()),
    path("album/<id>", AlbumDetailView.as_view()),

    path("group", GroupView.as_view()),
]