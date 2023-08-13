from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse
from nltk.lm import counter

from . import models

raw_user_symptoms = []
found_symptoms = []
counter_list = []
final_symptoms = []

class UserSymptomForm(forms.Form):
    symptomlist = forms.CharField(label="Symptoms(,):")

class SymptomOptionForm(forms.Form):
    choices = forms.CharField(label="Options(,):")

class CooccurringSymptomForm(forms.Form):
    cooccur = forms.CharField(label="Co-occurring symptoms:")

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
            global raw_user_symptoms
            raw_user_symptoms = models.rawpreprocessing(user_symptoms)
            global found_symptoms
            found_symptoms = models.initpreprocessing(raw_user_symptoms)
            return render(request, "predictionapp/displaysymptoms.html", {
                "symptoms": found_symptoms,
                "optionform": SymptomOptionForm()
            })
        else:
            # If the form is invalid, re-render the page with existing information
            return render(request, "predictionapp/usersymptoms.html", {
                "form": UserSymptomForm()
            })

def rawsymptoms(request):
    global raw_user_symptoms
    return render(request, "predictionapp/displaysymptoms.html", {
        "symptoms": raw_user_symptoms,
        "optionform": None
    })


def process_symptoms(request):
    if request.method == "GET":
        return render(request, "predictionapp/usersymptoms.html", {
            "form": UserSymptomForm()
        })
    elif request.method == "POST":
        form = SymptomOptionForm(request.POST)

        if form.is_valid():
            choices = form.cleaned_data["choices"]
            select_list = choices.split(",")
            global found_symptoms
            global counter_list
            global final_symptoms
            counter_list, final_symptoms = models.get_first_choice_symptoms(select_list, found_symptoms)
            return render(request, "predictionapp/cooccurring.html", {
                "symptoms": counter_list,
                "form": CooccurringSymptomForm()
            })
        else:
            return render(request, "predictionapp/usersymptoms.html", {
                "form": UserSymptomForm()
            })


def co_occurring(request):
    if request.method == "GET":
        return render(request, "predictionapp/cooccurring.html", {
            "symptoms": [],
            "form": CooccurringSymptomForm()
        })
    elif request.method == "POST":
        form = CooccurringSymptomForm(request.POST)

        if form.is_valid():
            cooccur = form.cleaned_data["cooccur"]
            select_list = cooccur.lower().split(",")
            global found_symptoms
            global counter_list
            global final_symptoms
            if select_list[0] == "no":
                pass
            else:
                for idx in select_list:
                    final_symptoms.append(found_symptoms[int(idx)])
            # Predict the disease
            diseases_list = models.predict_diseases(final_symptoms)

            return render(request, "predictionapp/finalsymptoms.html", {
                "symptoms": final_symptoms,
                "diseases": diseases_list
            })
