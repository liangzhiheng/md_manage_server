from django.urls import path

from video_manage.views import VideoDataView, LabelsView, LabelDetailView, VideoMetaView, VideoMetaDetailView, WatchView, PostersView


urlpatterns = [
    path("label", LabelsView.as_view()),
    path("label/<id>", LabelDetailView.as_view()),
    path("meta", VideoMetaView.as_view()),
    path("meta/<id>", VideoMetaDetailView.as_view()),
    path("data", VideoDataView.as_view()),
    path("<filename>", WatchView.as_view()),
    path("meta/posters/<id>", PostersView.as_view()),
]