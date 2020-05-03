from django.urls import include,path
from . import views

app_name = 'office'

urlpatterns = [
    path('', views.start, name='start'),
    path('issue/<int:pk>/', views.IssueDetailView.as_view(), name='issue'),
    path('issue/<int:pk>/addcomment', views.createcomment, name='createcomment'),
    path('issue/new/', views.IssueCreateView.as_view(), name='createissue'),
    path('issues', views.IssueListView.as_view(), name='issues'),
]
