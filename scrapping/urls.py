from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('craw/', views.crawPage),
    path('scrap/', views.scrapPage),
]