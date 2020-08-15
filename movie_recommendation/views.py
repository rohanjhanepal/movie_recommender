from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy ,reverse
from . import recommendmodel as mdl
import random

length = 0
search_data = []
data_main = []

def reset(request):
    global length , search_data , data_main
    request.session['sea'] = []
    length=0
    search_data=[]
    data_main=[]
    return redirect('movie_recommendation:home')


def index(request):
    
    context = {
        'data': mdl.tmdb_popular()
    }
    return render(request , 'movie_recommendation/index.html' , context=context)



def search(request):
    global length , search_data , data_main
    search_word = ''
    data = []
    
    if request.method == "POST":
        search_word = request.POST["search_word"]
        
        if(search_word in search_data):
            context = {
                'data': data_main,
                }
            return render(request , 'movie_recommendation/search.html' , context = context)
        #----------- Pass through ML model
        data = mdl.recommend_pro(search_word)
        
        if(data != None):
            data_main.extend(data[:4])
            search_data.append(search_word)
            request.session['sea'] = search_data
            length +=1
            data_main = [i for i in data_main if i not in search_data]
            if(len(data_main)>8):
                random.shuffle(data_main)
            context = {
                'data': data_main,
                }
        else:
            context = {
                'data': 'None',
            }
    
    return render(request , 'movie_recommendation/search.html' , context = context)
        
        