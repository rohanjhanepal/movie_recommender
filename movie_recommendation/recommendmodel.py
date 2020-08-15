import pandas as pd
import numpy
import random
from sklearn.feature_extraction.text import TfidfVectorizer as vectorizer
from sklearn.metrics.pairwise import sigmoid_kernel 
import os
from django.conf import settings
from difflib import SequenceMatcher as sm

from tmdbv3api import TMDb
from tmdbv3api import Movie , TV , Person

tmdb = TMDb()
tmdb.api_key = '182c8a83c58120ca7d6ca67eda867d86'

tmdb.language = 'en'
tmdb.debug = True

movie = Movie()
tv = TV()
person = Person()


base = 'https://image.tmdb.org/t/p/w1280/'

movie_df = None
sig = None
index =None

def tmdb_popular():
    global movie
    pop = []
    popular = movie.popular()
    for i , p in enumerate(popular):
        if(i > 6): return pop
        data = { 'title' : p.title ,
                 'overview': p.overview.split('.' , 2)[0],
                 'poster' : base+p.poster_path ,
                 'id': p.id ,
                 'vote' : p.vote_average
        }
        pop.append(data)
    return random.shuffle(pop)
    
    

def tmdb(name):
    global base , movie , tv 
    search = movie.search(name)
    if(len(search) ==0):
        search = tv.search(name)
        data = { 'title' : search[0].name ,
                 'overview': search[0].overview.split('.' , 2)[0],
                 'poster' : base+search[0].poster_path ,
                 'id': search[0].id ,
                 'vote' : search[0].vote_average
            }
    else:
        data = { 'title'    : search[0].title ,
                 'overview' : search[0].overview.split('.' , 2)[0] ,
                 'poster'   : base+search[0].poster_path ,
                 'id'       : search[0].id ,
                 'vote'     : search[0].vote_average ,
            }
    return data

def cast(name):
    p = person.details(name)
    print(p.biography)

def load_data():
    
    df = pd.read_csv(os.path.join(settings.BASE_DIR, 'learning_data/movies_tmdb.csv'))
    credits_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'learning_data/movies_tmdb_genres.csv'))
    net = pd.read_csv(os.path.join(settings.BASE_DIR, 'learning_data/netflix_titles.csv'))
    return [df , credits_df , net]
    
def pre_process():
    data = load_data()
    net = data[2]
    movie_df = pd.concat([data[0] , data[1]] , axis=1)
    df_net = pd.DataFrame(None , columns = ['title' , 'overview'])
    df_net['title'] = net['title']
    df_net['overview'] = net['description'] + net['listed_in'] 
    movie_df.drop(columns=['id' , 'original_lang','rel_date','popularity' , 'vote_count' , 'vote_average','Unnamed: 0'], axis = 1 , inplace = True)
    movie_df.drop(columns=['genre'] , axis = 1 , inplace = True)
    movie_df['title'] = movie_df['title'].apply(lambda x: str(x).lower())
    df_net['title'] = df_net['title'].apply(lambda x: str(x).lower())
    final = pd.concat([movie_df ,df_net] , axis =  0 ,ignore_index= True)
    final['overview'] = final['overview'].fillna('')
    return final



def process():
    global movie_df , sig , index
    movie_df = pre_process() 
    tfv = vectorizer(min_df=3 , max_features=None , strip_accents ='unicode' , analyzer='word'
        ,token_pattern = r'\w{1,}' ,
                ngram_range=(1,3),
                stop_words = 'english')
    tfv_matrix = tfv.fit_transform(movie_df['overview'])
    sig = sigmoid_kernel(tfv_matrix,tfv_matrix)
    index = pd.Series(movie_df.index, index=movie_df['title']).drop_duplicates()
    
def recommend(search_word):
    
    movie_df = pre_process() 
    tfv = vectorizer(min_df=3 , max_features=None , strip_accents ='unicode' , analyzer='word'
        ,token_pattern = r'\w{1,}' ,
                ngram_range=(1,3),
                stop_words = 'english')
    tfv_matrix = tfv.fit_transform(movie_df['overview'])
    sig = sigmoid_kernel(tfv_matrix,tfv_matrix)
    index = pd.Series(movie_df.index, index=movie_df['title']).drop_duplicates()
    
    
    try:
        title= search_word.lower()
        max_se = 0.0
        name = ''
        for i in list(movie_df['title']):
            se = sm(None , title , i)
            if(se.ratio() > max_se):
                name = i
                max_se = se.ratio()
        idx = index[name]
        if(type(idx) == pd.core.series.Series):
            print(type(idx) == pd.core.series.Series)
            idx = index[name]
            idx = idx[[random.randint(0,(len(idx)-1))]]
            idx = idx[name]
        else:
            idx = index[name]
        sig_scores = list(enumerate(sig[idx]))
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
        sig_scores = sig_scores[1:15]
        movie_indices = [i[0] for i in sig_scores]
        return list(movie_df['title'].iloc[movie_indices])
    except:
        return None


def recommend_pro(search_word):
    movie_list = recommend(search_word)
    if(movie_list == None):
        return None
    final =[]
    for i in movie_list:
        try:
            mov = tmdb(i)
            final.append(mov)
        except:
            pass
    return final