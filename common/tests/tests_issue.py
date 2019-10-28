from django.test import TestCase
from django.contrib.gis.geos import Point

from common.models import Issue, Category

class IssueModelTests(TestCase):
	def test_new_Issue(self):
		cat = Category(name = "test category")
		cat.save()
		issue = Issue(description = "test issue" , position = Point(5, 23), category = cat)
		issue.save()
		self.assertEqual(issue.id, 1)
		issue = Issue(id = 666, description = "test issue with defined id", position = Point(5, 23), category = cat)
		issue.save()
		self.assertEqual(issue.id, 666)
		
