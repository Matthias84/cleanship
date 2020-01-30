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
            description='A wip issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=True,
            assigned=group
        ).save()
        Issue(
            description='A wip issue',
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
            assigned=group
        ).save()
    
    def test_default_listing(self):
        """Service requests should look like"""
        client = APIClient()
        response = client.get('/citysdk/requests.json', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
