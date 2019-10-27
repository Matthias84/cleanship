from django.test import TestCase
from django.core.management.base import BaseCommand

from legacy.importer import import_issues
from common.models import Issue

class ImporterTests(TestCase):
	
	def test_import_csv_basic(self):
		"""Check if parsing a wellformed CSV works fine"""
		cmd = BaseCommand()
		import_issues(cmd, './legacy/tests/basic.csv')
		self.assertEqual(Issue.objects.count(), 8)
		
