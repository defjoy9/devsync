# notes/urls.py
from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('graph/', views.graph_page, name='graph_page'),
    path('graph/api/', views.graph_api, name='graph_api'),
    path('<slug:slug>/', views.note_detail, name='note_detail'),
]