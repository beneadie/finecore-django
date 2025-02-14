from django.urls import path
from . import views

from .ninjaAPI import api

urlpatterns = [
    path("ninjaAPI/", api.urls)
]
