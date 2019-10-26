from django.test import TestCase

from common.models import Issue

class IssueModelTests(TestCase):
	def test_new_Issue(self):
		issue = Issue(description = "test issue")
		issue.save()
		self.assertEqual(issue.id, 1)
		issue = Issue(id = 666, description = "test issue with defined id")
		issue.save()
		self.assertEqual(issue.id, 666)
		
