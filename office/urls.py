from django.urls import path
from . import views

app_name = 'office'

urlpatterns = [
    path('', views.start, name='start'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue'),
    path('issues', views.IssueListView.as_view(), name='issues')
]
