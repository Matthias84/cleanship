from django.conf.urls import url, include
from common.models import Issue, StatusTypes
from rest_framework import routers, serializers, viewsets

app_name = 'citysdk'

"""
We follow Open311 protocol design:
http://wiki.open311.org/GeoReport_v2/
This was extended by CitySDK participation:
https://www.citysdk.eu/citysdk-toolkit/using-the-apis/open311-api/
We also added some custom addons and simplicifations:
https://github.com/bfpi/klarschiff-citysdk

In short a endpoint provides following features:
- /citysdk/services.xml - listing all issue categories
- /citysdk/requests.xml - listing all (past) issues
- /citysdk/requests/x.xml - details for a submitted issue

The REST design allows read and write access.
"""

class IssueSerializer(serializers.ModelSerializer):
    """
    Transform issue to open311 service request
    
    service_request_id
    status_notes
    status
    service_code
    service_name
    description #status desr
    agency_responsible = 'string'
    service_notice
    requested_datetime
    updated_datetime
    # expected_datetime null
    address # null or location
    adress_id null
    lat
    long
    media_url #null or full HTTP url
    zipcode
    """
    service_request_id = serializers.IntegerField(source='id', read_only=True)
    status_notes = serializers.CharField(source="status_text", read_only=True)
    status = serializers.SerializerMethodField()
    service_code = serializers.PrimaryKeyRelatedField(source="category", read_only=True)
    service_name = serializers.CharField(source="category", read_only=True)
    description = serializers.CharField(read_only=True) # TODO: Contains also review state as string
    agency_responsible = serializers.CharField(source="assigned", read_only=True) # TODO: Needs to be a pretty full name
    service_notice = serializers.SerializerMethodField(read_only=True)
    requested_datetime = serializers.DateTimeField(source='created_at', read_only=True)
    updated_datetime = serializers.DateTimeField(source='status_created_at', read_only=True)
    address = serializers.CharField(source='location', read_only=True)
    adress_id = serializers.SerializerMethodField()
    media_url = serializers.ImageField(source='photo', use_url=True, read_only=True)
    
    class Meta:
        model = Issue
        fields = ['service_request_id', 'status_notes', 'status', 'service_code', 'service_name','description', 'agency_responsible', 'service_notice', 'requested_datetime', 'updated_datetime', 'address', 'adress_id', 'media_url']

    def get_status(self, obj):
        """Transform to 2 open311 status"""
        statusMap = {StatusTypes.SUBMITTED: 'open', StatusTypes.WIP: 'open', StatusTypes.SOLVED: 'closed', StatusTypes.IMPOSSIBLE: 'closed', StatusTypes.DUBLICATE: 'closed'}
        return statusMap[obj.status]

    def get_service_notice(self, obj):
        return None

    def get_adress_id(self, obj):
        return None

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all().order_by('-created_at')
    serializer_class = IssueSerializer

router = routers.DefaultRouter()
router.register(r'issues', IssueViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
