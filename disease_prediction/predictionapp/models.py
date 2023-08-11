from django.db import models

import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet

# Create your models here.

lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')

PATH = "/home/aneeshd/Desktop/COEP/TY/Sem6/DS/Project/Data-Science-Project-/preprocessing"

df_comb = pd.read_csv(PATH + "/dis_sym_dataset_comb.csv") # Disease combination
df_norm = pd.read_csv(PATH + "/dis_sym_dataset_norm.csv") # Individual Disease

X = df_norm.iloc[:, 1:]
Y = df_norm.iloc[:, 0:1]
# List of symptoms
dataset_symptoms = list(X.columns)

# returns the list of synonyms of the input word from 
# 1. thesaurus.com (https://www.thesaurus.com/), 
# 2. wordnet (https://www.nltk.org/howto/wordnet.html)
def synonyms(term):
    synonyms = []
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.content,  "html.parser")
    try:
        container=soup.find('section', {'class': 'MainContentContainer'})
        row=container.find('div',{'class':'css-191l5o0-ClassicContentCard'})
        row = row.find_all('li')
        for x in row:
            synonyms.append(x.get_text())
    except:
        None
    for syn in wordnet.synsets(term):
        synonyms+=syn.lemma_names()
    return set(synonyms)


def rawpreprocessing(user_symptoms):
    user_symptoms = user_symptoms.lower().split(",")
    # Preprocessing the input symptoms
    processed_user_symptoms = []
    for sym in user_symptoms:
        sym=sym.strip().replace('-',' ').replace("'",'')
        # TODO: Reduce
        sym = ' '.join([lemmatizer.lemmatize(word) for word in splitter.tokenize(sym)])
        processed_user_symptoms.append(sym)
    return processed_user_symptoms

from itertools import combinations
def initpreprocessing(raw_user_symptoms):
    # Taking each user symptom and finding all its synonyms and appending it to the pre-processed symptom string
    user_symptoms = []
    for user_sym in raw_user_symptoms:
        user_sym = user_sym.split()
        str_sym = set()
        for comb in range(1, len(user_sym)+1):
            for subset in combinations(user_sym, comb):
                subset=' '.join(subset)
                subset = synonyms(subset)
                str_sym.update(subset)
        str_sym.add(' '.join(user_sym))
        # query expansion performed by joining synonyms found for each symptoms
        # initially entered
        user_symptoms.append(' '.join(str_sym).replace('_',' '))

    # Loop over all the symptoms in dataset and check its similarity score to the synonym string of the user-input
    # symptoms. If similarity>0.5, add the symptom to the final list
    found_symptoms = set()
    for idx, data_sym in enumerate(dataset_symptoms):
        data_sym_split=data_sym.split()
        for user_sym in user_symptoms:
            count=0
            for symp in data_sym_split:
                if symp in user_sym.split():
                    count+=1
            if count/len(data_sym_split)>0.5:
                found_symptoms.add(data_sym)
    found_symptoms = list(found_symptoms)

    return found_symptoms
