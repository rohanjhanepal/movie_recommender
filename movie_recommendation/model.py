import pandas as pd
import numpy
import random
from sklearn.feature_extraction.text import TfidfVectorizer as vectorizer
from sklearn.metrics.pairwise import sigmoid_kernel 
import os
from django.conf import settings




def cleaner(d):
    test = d.split(',')
    f=''
    for i in test:
    
        if('name' in i):
            i= i.replace('name','')
            i= i.replace('\'\'','')
            i= i.replace(' ','')
            i= i.replace(':','')
            i= i.replace('\'','')
            i= i.replace('}','')
            i= i.replace(']','')
            i = i.replace('\"' , '')
            
            f+= i +' '
    return f



def load_data():
    
    df = pd.read_csv(os.path.join(settings.BASE_DIR, 'learning_data/movies_metadata_lite.csv'))
    credits_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'learning_data/credits_lite.csv'))
    return [df , credits_df]
    
def pre_process():
    data = load_data()
    movie_df = pd.concat([data[0] , data[1]] , axis=1)
    movie_df.drop(columns=['id'], axis = 1 , inplace = True)
    movie_df.drop(columns=['homepage' , 'budget'] , inplace = True)
    movie_df['overview'] = movie_df['overview'].fillna('')
    movie_df['genres'] = movie_df['genres'].apply(cleaner)
    movie_df['cast'] = movie_df['cast'].apply(cleaner)
    movie_df['cast'] = movie_df['cast'].apply(lambda x: ' '.join(x.split(' ')[:2]))
    movie_df['bow'] = movie_df['overview'] + movie_df['genres'] + movie_df['cast']
    
    return movie_df



def recommend(search_word):
    movie_df = pre_process()
    
    
    tfv = vectorizer(min_df=3 , max_features=None , strip_accents ='unicode' , analyzer='word'
        ,token_pattern = r'\w{1,}' ,
                ngram_range=(1,3),
                stop_words = 'english')
    tfv_matrix = tfv.fit_transform(movie_df['bow'])
    sig = sigmoid_kernel(tfv_matrix,tfv_matrix)
    index = pd.Series(movie_df.index, index=movie_df['original_title']).drop_duplicates()
    
    try:
        idx = index[search_word]
        sig_scores = list(enumerate(sig[idx]))
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
        sig_scores = sig_scores[1:15]
        movie_indices = [i[0] for i in sig_scores]

        return list(movie_df['original_title'].iloc[movie_indices])
    except:
        return None

