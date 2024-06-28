"""
URL configuration for md_manage_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from video_manage.urls import urlpatterns
from user_manage.urls import urlpatterns
from audio_manage.urls import urlpatterns

urlpatterns = [
    path('video/', include('video_manage.urls')),
    path('user/', include('user_manage.urls')),
    path('label', include('labels_manage.urls')),
    path("audio/", include("audio_manage.urls")),
]
