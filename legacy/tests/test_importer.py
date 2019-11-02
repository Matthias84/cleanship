from django.test import TestCase
from django.core.management.base import BaseCommand

from legacy.importer import IssueImporter, CategoryImporter
from common.models import Issue, Category


class ImporterTests(TestCase):

    def test_import_csv_issues_basic(self):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        for x in range(1, 8):
            cat = Category(id=x, name='A' + str(x), parent=catA)
            cat.save()
        ii = IssueImporter(cmd, './legacy/tests/basic.csv')
        self.assertEqual(Issue.objects.count(), 8)
    
    def test_import_csv_issues_chunks(self):
        """Check splitting import in chunks"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        for x in range(1, 8):
            cat = Category(id=x, name='A' + str(x), parent=catA)
            cat.save()
        ii = IssueImporter(cmd, './legacy/tests/basic.csv', chunkSize=3)
        self.assertEqual(Issue.objects.count(), 8)

    def test_import_csv_categories_basic(self):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        ci = CategoryImporter(cmd, './legacy/tests/basic-cat.csv')
        self.assertEqual(Category.objects.count(), 11)

    def test_import_csv_categories_clean(self):
        """Check if clean removes existing objects"""
        cat = Category(name='Testcategory')
        cat.save()
        cmd = BaseCommand()
        ci = CategoryImporter(cmd, './legacy/tests/basic-cat.csv')
        self.assertEqual(Category.objects.count(), 11)
