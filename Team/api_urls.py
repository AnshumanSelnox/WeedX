from django.urls import path
from .views import *
urlpatterns = [

    path('RegisterAPI/', RegisterAPI.as_view()),






]
