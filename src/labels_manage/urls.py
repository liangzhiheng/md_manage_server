from django.urls import path

from labels_manage.views import LabelsView, LabelDetailView

urlpatterns = [
    path('/', LabelsView.as_view()),
    path('/<id>', LabelDetailView.as_view()),
]