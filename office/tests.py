from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta
from unittest.mock import patch

from .views import start
from common.models import User, Issue, Category, StatusTypes

# Testing office views

@patch("common.models.get_landowner")
@patch("requests.post")
class OfficeStartViewTests(TestCase):

    def test_start_no_login(self, requests_post, get_landowner):
        """Is view save?"""
        response = self.client.get(reverse('office:start'))
        self.assertRedirects(response, reverse('login')+'?next=%2Foffice%2F')

    def test_start_login(self, requests_post, get_landowner):
        """Can we successfully login?"""
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('office:start'))
        self.assertEqual(response.status_code, 200)
    
    def test_start_qa(self, requests_post, get_landowner):
        """Do we find all QA critical issues?"""
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        group = Group(name='testers')
        group.save()
        group.user_set.add(tester)
        group.save()
        cat = Category(name='test cat')
        cat.save()
        requests_post.json.return_value = {'features': []}
        get_landowner.return_value = 'TEST landowner'
        Issue(
            description='A old issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now() - timedelta(days = 30),
            status=StatusTypes.WIP,
            published=False,
            assigned=group
        ).save()
        Issue(
            description='Another old issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now() - timedelta(days = 20),
            status=StatusTypes.WIP,
            published=False,
            assigned=group
        ).save()
        Issue(
            description='Unassigned issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now() - timedelta(days = 20),
            status=StatusTypes.WIP,
            published=False,
        ).save()
        Issue(
            description='Very new issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=False,
            assigned=group
        ).save()
        Issue(
            description='Unupdated issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now() - timedelta(days = 35),
            status=StatusTypes.WIP,
            status_created_at=timezone.now() - timedelta(days = 35),
            published=True,
            assigned=group
        ).save()
        # Check if we get only old unreviewed issues back
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('office:start'))
        qs = response.context['issues3dunchecked']
        self.assertEqual(len(qs), 2)
        qs = response.context['issues30dunupdated']
        self.assertEqual(len(qs), 1)

@patch("common.models.get_landowner")
@patch("requests.post")
class OfficeListViewTests(TestCase):
    
    def test_issues_no_login(self, requests_post, get_landowner):
        """Is view save?"""
        response = self.client.get(reverse('office:issues'))
        self.assertRedirects(response, reverse('login')+'?next=%2Foffice%2Fissues')

    def test_issues_login(self, requests_post, get_landowner):
        """Can we successfully login?"""
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('office:issues'))
        self.assertEqual(response.status_code, 200)

    def test_issues_assigned(self, requests_post, get_landowner):
        """Do we find all QA critical issues?"""
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        self.client.login(username='tester', password='test')
        group = Group(name='testers')
        group.save()
        group.user_set.add(tester)
        group.save()
        cat = Category(name='test cat')
        cat.save()
        requests_post.json.return_value = {'features': []}
        get_landowner.return_value = 'TEST landowner'
        Issue(
            description='my issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=True,
            assigned=group
        ).save()
        Issue(
            description='other issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=True,
            assigned=None
        ).save()
        response = self.client.get(reverse('office:issues'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['issue_list']), 1)

@patch("common.models.get_landowner")
@patch("requests.post")
class OfficeDetailViewTests(TestCase):

    def test_detail_no_login(self, requests_post, get_landowner):
        """Is view save?"""
        response = self.client.get(reverse('office:issue', kwargs={'pk': 0}))
        self.assertRedirects(response, reverse('login')+'?next=%2Foffice%2Fissue%2F0%2F')

    def test_detail_login(self, requests_post, get_landowner):
        """Can we successfully login?"""
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        self.client.login(username='tester', password='test')
        response = self.client.get(reverse('office:issue', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, 404)
    
    def test_detail_assigned(self, requests_post, get_landowner):
        tester = User(username='tester', password=make_password('test'))
        tester.save()
        self.client.login(username='tester', password='test')
        group = Group(name='testers')
        group.save()
        group.user_set.add(tester)
        group.save()
        cat = Category(name='test cat')
        cat.save()
        requests_post.json.return_value = {'features': []}
        get_landowner.return_value = 'TEST landowner'
        myIssue=Issue(
            description='My issue',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=False,
            assigned=group
        )
        myIssue.save()
        response = self.client.get(reverse('office:issue', kwargs={'pk': myIssue.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], myIssue)
        # Everybody should at least read
        otherIssue=Issue(
            description='Not mine',
            position=Point(54.1, 12.1, srid=4326),
            category=cat,
            created_at=timezone.now(),
            status=StatusTypes.WIP,
            published=False,
            assigned=group
        )
        otherIssue.save()
        response = self.client.get(reverse('office:issue', kwargs={'pk': otherIssue.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issue'], otherIssue)
        
        
