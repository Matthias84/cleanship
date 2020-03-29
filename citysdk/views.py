from django.conf.urls import url, include
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext_lazy as _
from common.models import Issue, Category, StatusTypes, TrustTypes
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response

from .serializers import IssueSerializer, CategorySerializer

"""
For legacy support to the public Klarschiff Frontends,
this REST API allows fetching issues as JSON

We follow CitySDK paritication protocol design:
https://www.citysdk.eu/citysdk-toolkit/using-the-apis/open311-api/
This is an extension to the Open311 specification:
http://wiki.open311.org/GeoReport_v2/
We also added some custom addons and simplicifations:
https://github.com/bfpi/klarschiff-citysdk

In short a endpoint provides following features:
- /citysdk/services.json - listing all issue categories
- /citysdk/requests.json - listing all (past) issues
- /citysdk/requests/x.json - details for a submitted issue
(- /citysdk/areas.json - list geometries to subscribe for custom observations)
(- /citysdk/discovery.json - enumerate all of your public endpoints)
"""

    

class IssueViewSet(viewsets.ModelViewSet):
    """
    Encapsulate all API calls related to Open311 service requests / issues
    Offers filters and returns JSON serialized requests
    e.g. https://www.klarschiff-hro.de/citysdk/requests.json?detailed_status=RECEIVED%2C+IN_PROCESS%2C+PROCESSED%2C+REJECTED&extensions=true&keyword=problem%2C+idea&max_requests=6&with_picture=true
    """
    serializer_class = IssueSerializer
    
    # TODO: Add api_key permissions
    
    def get_paginated_response(self, data):
        # Redefined to avoid JSON extra pagination fields
        return Response(data)
    
    def get_queryset(self):
        query_params = self.request.query_params
        # TODO: Security Check the filterstrings
        max_requests = query_params.get('max_requests', None) # TODO: What is CitySDK default limit?
        also_archived = query_params.get('also_archived', 'false')
        start_date = query_params.get('start_date', None)
        end_date = query_params.get('end_date', None)
        lat = query_params.get('lat', None)
        long = query_params.get('long', None)
        radius = query_params.get('radius', None)
        keywords = query_params.get('keyword', None)
        with_picture = query_params.get('with_picture', None)
        queryStatusCitySDK = query_params.get('detailed_status', None)
        # TODO: params just_count
        # (updated_after, updated_before)
        # (agency_responsible)
        if also_archived.lower() == 'true': # TODO: Adapt to new depublish flag?
            queryset_list = Issue.objects.all().order_by('-created_at')
        else:
            queryset_list = Issue.objects.filter(published=True).order_by('-created_at')
        if start_date and end_date:
            queryset_list = queryset_list.filter(created_at__range=[start_date, end_date])
        else:
            if start_date:
                queryset_list = queryset_list.filter(created_at__gte=start_date)
            if end_date:
                queryset_list = queryset_list.filter(created_at__lte=end_date)
        if keywords:
            # Limit by type (old Klarschiff uses keywords list)
            keywords=keywords.lower()
            if 'idee' in keywords:
                catidee = Category.get_ideas_root()
                queryset_list = queryset_list.filter(category__in=catidee.get_descendants())
            if 'problem' in keywords:
                catproblem = Category.get_problem_root()
                queryset_list = queryset_list.filter(category__in=catproblem.get_descendants())        
        if queryStatusCitySDK:
            # Limit by status list
            queryStatus =  []
            statusMap = {'RECEIVED': StatusTypes.SUBMITTED, 'IN_PROCESS': StatusTypes.WIP, 'PROCESSED':StatusTypes.SOLVED, 'REJECTED':StatusTypes.IMPOSSIBLE, 'closed': StatusTypes.DUBLICATE}
            for x in queryStatusCitySDK.split(','):
                queryStatus.append(statusMap[x])
            # Review is mapped as IN_PROCESS as well
            if StatusTypes.WIP in queryStatus:
                queryStatus.append(StatusTypes.REVIEW)
            queryset_list = queryset_list.filter(status__in = queryStatus)
        if with_picture:
            # Limit if photo present
            if with_picture.lower() == 'true':
                queryset_list = queryset_list.exclude(photo__exact='')
        if lat and long and radius:
            # Limit by surrounding geo bbox
            pnt = GEOSGeometry('POINT({} {})'.format(lat, long), srid=4326)
            print(pnt)
            # TODO: Make sure internal CRS is projected -> metrical
            # TODO: Limiting size for requests ?
            queryset_list = queryset_list.filter(position__distance_lte=(pnt, D(m=float(radius))))
        if max_requests:
            # Limit by amount
            queryset_list = queryset_list[:int(max_requests)]
        return queryset_list

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Encapsulate all API calls related to Open311 services / categories
    We map our 3-level hierachy using the keyword, group references
    e.g. https://www.klarschiff-hro.de/citysdk/services.json
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(level=2)
    
    def get_paginated_response(self, data):
        # Redefined to avoid JSON extra pagination fields
        return Response(data)
