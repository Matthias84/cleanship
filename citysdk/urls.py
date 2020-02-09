from django.conf.urls import url, include
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext_lazy as _
from common.models import Issue, Category, StatusTypes, TrustTypes
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response

from .serializers import IssueSerializer, CategorySerializer
from .views import IssueViewSet, CategoryViewSet

app_name = 'citysdk'

router = routers.DefaultRouter()
router.register(r'requests', IssueViewSet, basename='issues')
router.register(r'services', CategoryViewSet, basename='categories')
# TODO: Security Check that we don't leak non public infos

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
