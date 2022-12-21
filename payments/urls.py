from django.urls import path
from .views import *

urlpatterns = [
    path('pay',HomePageView.as_view(),name='pay'),
    path('charge/',charge,name='charge')
]