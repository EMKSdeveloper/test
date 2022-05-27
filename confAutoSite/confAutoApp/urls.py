from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submitting/', views.submitting, name = 'submitting'),
    #path('authorized/', views.authorized, name = 'authorized'),
]