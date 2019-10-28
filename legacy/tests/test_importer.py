from django.test import TestCase
from django.core.management.base import BaseCommand

from legacy.importer import import_issues, import_cat
from common.models import Issue, Category

class ImporterTests(TestCase):
	
	def test_import_csv_basic(self):
		"""Check if parsing a wellformed CSV works fine"""
		cmd = BaseCommand()
		catA = Category(id = 0, name = 'Category A')
		catA.save()
		for x in range(1, 8):
			cat = Category(id = x, name = 'A'+str(x), parent = catA)
			cat.save()
		import_issues(cmd, './legacy/tests/basic.csv')
		self.assertEqual(Issue.objects.count(), 8)
		
	def test_import_csv_categories_basic(self):
		"""Check if parsing a wellformed CSV works fine"""
		cmd = BaseCommand()
		import_cat(cmd, './legacy/tests/basic-cat.csv')
		self.assertEqual(Category.objects.count(), 11)
