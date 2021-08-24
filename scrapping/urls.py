from django.urls import path
from . import views

urlpatterns = [
    path('', views.index), #여기서 ("경로설정", "views.무슨 함수 호출할지")
    path('craw/', views.crawPage),
    path('scrap/', views.scrapPage),
    path('export/', views.exportCSV),
    path('nlp/', views.konlpy),
    # path('pandas/', views.pandas),
]