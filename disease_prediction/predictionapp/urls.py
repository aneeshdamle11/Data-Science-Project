from django.urls import path
from . import views

app_name = "predictionapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("usersymptoms", views.usersymptoms, name="usersymptoms")
]
