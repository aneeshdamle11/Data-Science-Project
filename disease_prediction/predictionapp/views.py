from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from . import models

class UserSymptomForm(forms.Form):
    symptomlist = forms.CharField(label="Cough, Cold, Head pain")

# Create your views here.

def index(request):
    return HttpResponse(b"Hello, world!")

def usersymptoms(request):
    # GET method
    if request.method == "GET":
        return render(request, "predictionapp/usersymptoms.html", {
            "form": UserSymptomForm()
        })
    # POST method
    elif request.method == "POST":
        form = UserSymptomForm(request.POST)

        if form.is_valid():
            # Taking symptoms from user as input
            user_symptoms = form.cleaned_data["symptomlist"]
            processed_user_symptoms = models.rawpreprocessing(user_symptoms)
            return render(request, "predictionapp/displayraw.html", {
                "symptoms": processed_user_symptoms
            })
        else:
            # If the form is invalid, re-render the page with existing information
            return render(request, "predictionapp/usersymptoms.html", {
                "form": UserSymptomForm()
            })

