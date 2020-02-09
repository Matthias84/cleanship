from django.test import TestCase
from unittest.mock import patch
from django.contrib.gis.geos import Point

from common.models import Issue, Category

@patch("common.models.get_landowner")
@patch("requests.post")
class IssueModelTests(TestCase):
    def test_new_Issue(self, requests_post, get_landowner):
        """
        Can we create specific issues?
        """
        #requests_post.status_code.return_value = 200
        requests_post.json.return_value = {'features': []}
        get_landowner.return_value = 'TEST landowner'
        cat = Category(name="test category")
        cat.save()
        issue = Issue(description="test issue", position=Point(5, 23), category=cat)
        issue.save()
        self.assertEqual(len(Issue.objects.all()), 1)
        issue = Issue(id=666, description="test issue with defined id", position=Point(5, 23), category=cat)
        issue.save()
        self.assertEqual(issue.id, 666)
