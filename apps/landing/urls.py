from django.urls import path, include
from . import views

app_name='landing'

urlpatterns = [
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'),
    path('funcionalidades/', views.funcionalidades, name='funcionalidades')
]
