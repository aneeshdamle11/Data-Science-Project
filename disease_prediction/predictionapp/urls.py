from django.urls import path
from . import views

app_name = "predictionapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("usersymptoms", views.usersymptoms, name="usersymptoms"),
    path("rawsymptoms", views.rawsymptoms, name="rawsymptoms"),
    path("process_symptoms", views.process_symptoms, name="process_symptoms"),
    path("co-occurring", views.co_occurring, name="co_occurring")
]
