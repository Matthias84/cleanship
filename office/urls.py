from django.urls import path
from . import views

app_name = 'office'

urlpatterns = [
    path('', views.start, name='start'),
]
