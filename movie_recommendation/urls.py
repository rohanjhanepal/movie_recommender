from django.urls import path , include
from . import views

app_name = 'movie_recommendation'

urlpatterns = [
    
    path('', views.index , name = 'home' ),
    path('search/', views.search , name = 'search' ),
    path('reset/', views.reset , name = 'reset' ),
]

