from django.db import models

# Create your models here.
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')

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

