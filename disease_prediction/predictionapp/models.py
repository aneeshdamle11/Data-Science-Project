from django.db import models
import pandas as pd
import requests, operator, os
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet
from itertools import combinations
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from statistics import mean

# Create your models here.

lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')

PATH = os.environ['PWD'] + "/data"

df_comb = pd.read_csv(PATH + "/dis_sym_dataset_comb.csv") # Disease combination
df_norm = pd.read_csv(PATH + "/dis_sym_dataset_norm.csv") # Individual Disease
X = df_comb.iloc[:, 1:]
Y = df_comb.iloc[:, 0:1]

# Logistic Regressor Classifier
lr = LogisticRegression()
lr = lr.fit(X, Y)
scores = cross_val_score(lr, X, Y, cv=5)

X = df_norm.iloc[:, 1:]
Y = df_norm.iloc[:, 0:1]

# List of symptoms
dataset_symptoms = list(X.columns)

DISEASES_COUNT = 10

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


def get_first_choice_symptoms(select_list, found_symptoms):
    dis_list = set()
    final_symptoms = []
    counter_list = []
    for idx in select_list:
        symp=found_symptoms[int(idx)]
        final_symptoms.append(symp)
        dis_list.update(set(df_norm[df_norm[symp]==1]['label_dis']))

    for dis in dis_list:
        row = df_norm.loc[df_norm['label_dis'] == dis].values.tolist()
        row[0].pop(0)
        for idx,val in enumerate(row[0]):
            if val!=0 and dataset_symptoms[idx] not in final_symptoms:
                counter_list.append(dataset_symptoms[idx])
    return counter_list, final_symptoms


def get_dict_counterlist(counter_list):
    # Symptoms that co-occur with the ones selected by user
    dict_symp = dict(Counter(counter_list))
    dict_symp_tup = sorted(dict_symp.items(), key=operator.itemgetter(1),reverse=True)
    return dict_symp_tup


def predict_diseases(final_symp):
    sample_x = [0 for x in range(0,len(dataset_symptoms))]
    for val in final_symp:
        sample_x[dataset_symptoms.index(val)]=1

    # Predict disease
    lr = LogisticRegression()
    lr = lr.fit(X, Y)
    prediction = lr.predict_proba([sample_x])
    k = DISEASES_COUNT
    diseases = list(set(Y['label_dis']))
    diseases.sort()
    topk = prediction[0].argsort()[-k:][::-1]

    topk_dict = {}
    # Show top 10 highly probable disease to the user.
    fp = open("disease_output.csv", "w")
    fp.write("Disease, Percentage\n")
    for idx,t in  enumerate(topk):
        match_sym=set()
        row = df_norm.loc[df_norm['label_dis'] == diseases[t]].values.tolist()
        row[0].pop(0)

        for idx,val in enumerate(row[0]):
            if val!=0:
                match_sym.add(dataset_symptoms[idx])
        prob = (len(match_sym.intersection(set(final_symp)))+1)/(len(set(final_symp))+1)
        prob *= mean(scores)
        topk_dict[t] = prob

    j = 0
    topk_index_mapping = {}
    topk_sorted = dict(sorted(topk_dict.items(), key=lambda kv: kv[1], reverse=True))

    diseases_list = []
    for key in topk_sorted:
        prob = topk_sorted[key]*100
        diseases_list.append(diseases[key] + "\tProbability:" + str(round(prob, 2)) + "%")
        fp.write(f"{diseases[key]}, {str(round(prob, 2))}\n")
        topk_index_mapping[j] = key
        j += 1

    fp.close()

    return diseases_list
