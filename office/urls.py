from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='office_start'),
]
