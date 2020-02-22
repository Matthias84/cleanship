from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient
from unittest.mock import patch

from common.models import User, Issue, Category, StatusTypes

"""
We check our implementation against Klarschiff CitySDK extended specs.
This includes:
- URL schema
- JSON response payload
- HTTP filter params

see https://github.com/bfpi/klarschiff-citysdk
and implementation at https://www.klarschiff-hro.de/citysdk/...
"""

class CitySDKRequestsTests(TestCase):
    
    @patch("common.models.get_landowner")
    @patch("requests.post")
    def setUp(self, requests_post, get_landowner):
        group = Group(name='testers')
        group.save()
        cat = Category(name='test cat')
        cat.save()
        # we fake some 3rd party API calls
        requests_post.json.return_value = {'features': []}
        get_landowner.return_value = 'TEST landowner'
        # our test issues
        Issue(
            id=0,
            description='A wip issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=True,
            assigned=group
        ).save()
        Issue(
            description='A very fresh issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.SUBMITTED,
            published=True,
            assigned=group
        ).save()
        Issue(
            description='A old finished issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.SOLVED,
            published=False,
            assigned=group,
            photo='testphoto.jpg'
        ).save()
    
    def test_default_listing_filter(self):
        """Do we get only active requests?"""
        client = APIClient()
        response = client.get('/citysdk/requests.json?extensions=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_default_listing_content(self):
        """Do we get only active requests?"""
        client = APIClient()
        response = client.get('/citysdk/requests.json?extensions=true')
        self.assertEqual(response.status_code, 200)
        # Adapted dict from https://www.klarschiff-hro.de/citysdk/requests.json
        activeRequests = [
            {"service_request_id":0,"extended_attributes":{"detailed_status":"IN_PROCESS","detailed_status_datetime":"2020-01-30T21:52:55.000+01:00","description_public":True,"media_urls":[],"photo_required":True,"trust":1,"votes":0},"status_notes":"Ihre Meldung wurde zur Beräumung des Sperrmülls an die Stadtentsorgung Rostock weitergeleitet!","status":"open","service_code":"29","service_name":"Sperrmüll","description":"Gegenüber der Bleicherstr.31 befindet sich ein Sperrmüllhaufen!","agency_responsible":"Amt für Umweltschutz (delegiert an Stadtentsorgung Rostock GmbH)","service_notice":None,"requested_datetime":"2020-01-30T21:52:47.000+01:00","updated_datetime":"2020-01-30T21:53:31.000+01:00","expected_datetime":"2020-01-31T00:00:00.000+01:00","address":"Bleicherstr. 31 (gegenüber)","adress_id":None,"lat":"54.084745606995064","long":"12.145760492171316","media_url":None,"zipcode":None},
            {"service_request_id":51578,"extended_attributes":{"detailed_status":"RECEIVED","detailed_status_datetime":"2020-01-30T17:07:46.000+01:00","description_public":False,"media_urls":["http://www.klarschiff-hro.de/citysdk/assets/fotoGross-ed651ba3192856892dfee19b3a099cefdfa35298decd5f6253905403d8045f9a.jpg","http://www.klarschiff-hro.de/citysdk/assets/fotoNormal-8953f1d3359b95db912f315c0b0f6d10e4b4b92ad45d332f85a8829b6f74330e.jpg","http://www.klarschiff-hro.de/citysdk/assets/fotoThumb-55401594568590516a7459e1308150acf164e47e30aebf757871aa76d735d07c.jpg"],"photo_required":False,"trust":0,"votes":0},"status_notes":None,"status":"open","service_code":"5","service_name":"bauliche Gefahrenstelle","description":"redaktionelle Prüfung ausstehend","agency_responsible":"Amt für Verkehrsanlagen","service_notice":None,"requested_datetime":"2020-01-30T17:07:03.000+01:00","updated_datetime":"2020-01-30T17:07:46.000+01:00","expected_datetime":None,"address":"Max-Reichpietsch-Str. 8","adress_id":None,"lat":"54.19408178460182","long":"12.151084000915997","media_url":"http://www.klarschiff-hro.de/citysdk/assets/fotoNormal-8953f1d3359b95db912f315c0b0f6d10e4b4b92ad45d332f85a8829b6f74330e.jpg","zipcode":None}
        ]
        #self.assertEqual(response.data, activeRequests)

    def test_details(self):
        """Do we get request details as JSON?"""
        client = APIClient()
        response = client.get('/citysdk/requests/0.json')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({"service_request_id":0, "media_url":None, "status":"open", "adress_id":None,"zipcode":None }, response.data, )
    
class CitySDKServicesTests(TestCase):
    
    def setUp(self):
        # Create a 3 level cat hierachy
        ideen = Category(name=Category.IDEA)
        ideen.save()
        mainCat = Category(name='main cat', parent=ideen)
        mainCat.save()
        catA = Category(name='test sub cat A', parent=mainCat)
        catA.save()
        catB = Category(name='test sub cat B', parent=mainCat)
        catB.save()
    
    def test_default_listing(self):
        """Do we get all categories?"""
        client = APIClient()
        response = client.get('/citysdk/services.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # adapted dict from https://www.klarschiff-hro.de/citysdk/services.json
        self.assertDictEqual({"service_code":"6","service_name":"test sub cat A","description":None,"metadata":False,"type":"realtime","keywords":"idee","group":"main cat"}, dict(response.data[0]))

