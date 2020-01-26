from django.conf.urls import url, include
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext_lazy as _
from common.models import Issue, Category, StatusTypes, TrustTypes
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response

app_name = 'citysdk'

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

class NestedExtendedAttributesSerializer(serializers.Serializer):
    """
    Add most CitySDK extensions below sub-element 'extended_attributes'
    """
    detailed_status = serializers.SerializerMethodField(read_only=True)
    detailed_status_datetime = serializers.DateTimeField(source='status_created_at', read_only=True)
    description_public = serializers.SerializerMethodField(read_only=True)
    media_urls = serializers.SerializerMethodField(read_only=True)
    photo_required = serializers.SerializerMethodField(read_only=True)
    trust = serializers.SerializerMethodField(read_only=True)
    votes = serializers.SerializerMethodField(read_only=True)
    
    def get_detailed_status(self, obj):
        """Transform to citySDK status"""
        statusMap = {StatusTypes.SUBMITTED: 'RECEIVED', StatusTypes.WIP: 'IN_PROCESS', StatusTypes.SOLVED: 'PROCESSED', StatusTypes.IMPOSSIBLE: 'REJECTED', StatusTypes.DUBLICATE: 'closed'}
        # TODO: Map PENDING if we add review state
        return statusMap[obj.status]
    
    def get_description_public(self, obj):
        # TODO: Fix if we can depublish issue description
        return True
    
    def get_media_urls(self, obj):
        """Get photo arrays with same HTTP(S) protocol"""
        # TODO: Fix if we integrate thumbnails
        if obj.photo:
            request = self.context.get('request')
            photo_url = request.build_absolute_uri(obj.photo.url)
            ret = {
                "0": photo_url, # big one
                "1": photo_url, # normal one
                "2": photo_url, # small one
            }
        else:
            return []
        return ret
    
    def get_photo_required(self, obj):
        # TODO: Fix if we integrate issue photo requests
        return False
    
    def get_trust(self, obj):
        """Transform to int trust level"""
        # TODO: Fix if we store issue.trust
        # trustMap = {TrustTypes.EXTERNAL: 0, TrustTypes.INTERNAL: 1, TrustTypes.FIELDTEAM: 2}
        # return trustMap[obj.trust]
        return 0
    
    def get_votes(self, obj):
        # TODO: Fix if we store votes
        return 0

class IssueSerializer(serializers.ModelSerializer):
    """
    Transform issue to open311 service request
    """
    # TODO: We assume exteded_attributes=True
    address = serializers.CharField(source='location', read_only=True)
    adress_id = serializers.SerializerMethodField(read_only=True)
    agency_responsible = serializers.SerializerMethodField()
    extended_attributes = NestedExtendedAttributesSerializer(source='*')
    lat = serializers.SerializerMethodField(read_only=True)
    long = serializers.SerializerMethodField(read_only=True)
    media_url = serializers.ImageField(source='photo', use_url=True, read_only=True)
    service_code = serializers.PrimaryKeyRelatedField(source="category", read_only=True)
    service_name = serializers.CharField(source="category", read_only=True)
    status_notes = serializers.CharField(source="status_text", read_only=True)
    service_notice = serializers.SerializerMethodField(read_only=True)
    service_request_id = serializers.IntegerField(source='id', read_only=True)
    status = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True) # TODO: Contains also review state as string
    expected_datetime = serializers.SerializerMethodField(read_only=True)
    requested_datetime = serializers.DateTimeField(source='created_at', read_only=True)
    updated_datetime = serializers.DateTimeField(source='status_created_at', read_only=True)
    zipcode = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Issue
        fields = [   # Order is same as legacy Klarschiff CitySDK
                    'service_request_id',
                    'extended_attributes',
                    'status_notes',
                    'status',
                    'service_code',
                    'service_name',
                    'description',
                    'agency_responsible',
                    'service_notice',
                    'requested_datetime',
                    'updated_datetime',
                    'expected_datetime',
                    'address',
                    'adress_id',
                    'lat', 'long',
                    'media_url',
                    'zipcode'
        ]

    def get_status(self, obj):
        """Transform to 2 open311 status"""
        statusMap = {StatusTypes.SUBMITTED: 'open', StatusTypes.WIP: 'open', StatusTypes.SOLVED: 'closed', StatusTypes.IMPOSSIBLE: 'closed', StatusTypes.DUBLICATE: 'closed'}
        return statusMap[obj.status]

    def get_long(self, obj):
        """WGS84 x as string"""
        return str(obj.get_position_WGS84().x)

    def get_lat(self, obj):
        """WGS84 y as string"""
        return str(obj.get_position_WGS84().y)

    def get_service_notice(self, obj):
        # Not used, but required by citySDK spec
        return None

    def get_adress_id(self, obj):
        # Not used, but required by citySDK spec
        return None

    def get_expected_datetime(self, obj):
        # Not used, but required by citySDK spec
        return None
        
    def get_zipcode(self, obj):
        # Not used, but required by citySDK spec
        return None
    
    def get_agency_responsible(self, obj):
        if obj.assigned:
            if obj.delegated:
                # TODO: Needs to be a pretty full name
                return _('{} (delegated to {})').format(obj.assigned.name, obj.delegated.name)
            else:
                return obj.assigned.name

class CategorySerializer(serializers.ModelSerializer):
    service_code = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.CharField(source='name', read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    metadata = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    keywords = serializers.SerializerMethodField(read_only=True)
    group = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Category
        fields = [   # Order is same as legacy Klarschiff CitySDK
                    'service_code',
                    'service_name',
                    'description',
                    'metadata',
                    'type',
                    'keywords',
                    'group'
        ]
        
    def get_keywords(self, category):
        # Like Klarschiff, we map Level 0 (idee / problem / tipp via keyword
        return category.get_root().name.lower()

    def get_group(self, category):
        # Like Klarschiff, we map Level 1 maincategories
        return category.parent.name
        
    def get_service_code(self, category):
        # We use (imported) Klarschiff category IDs
        return str(category.id)
    
    def get_type(self, category):
        # Not used, but required by citySDK spec
        return "realtime"

    def get_description(self, category):
        # Not used, but required by citySDK spec
        return None
    
    def get_metadata(self, category):
        # Not used, but required by citySDK spec
        return False
    

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
                catidee = Category.objects.filter(name='Idee').first()
                queryset_list = queryset_list.filter(category__in=catidee.get_descendants())
            if 'problem' in keywords:
                catidee = Category.objects.filter(name='Problem').first()
                queryset_list = queryset_list.filter(category__in=catidee.get_descendants())        
        if queryStatusCitySDK:
            # Limit by status list
            queryStatus =  []
            statusMap = {'RECEIVED': StatusTypes.SUBMITTED, 'IN_PROCESS': StatusTypes.WIP, 'PROCESSED':StatusTypes.SOLVED, 'REJECTED':StatusTypes.IMPOSSIBLE, 'closed': StatusTypes.DUBLICATE}
            for x in queryStatusCitySDK.split(','):
                queryStatus.append(statusMap[x])
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

router = routers.DefaultRouter()
router.register(r'requests', IssueViewSet, basename='issues')
router.register(r'services', CategoryViewSet, basename='categories')
# TODO: Security Check that we don't leak non public infos

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
