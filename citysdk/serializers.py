from django.conf.urls import url, include
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext_lazy as _
from common.models import Issue, Category, StatusTypes, TrustTypes
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response

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
