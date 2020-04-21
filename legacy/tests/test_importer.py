from django.test import TestCase
from unittest.mock import patch
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from legacy.importer import IssueImporter, CategoryImporter, CommentImporter, FeedbackImporter, UserImporter
from common.models import Issue, Category, Comment, Feedback, User, Group

@patch("common.models.get_landowner")
@patch("requests.post")
class ImporterTests(TestCase):

    def test_import_csv_issues_basic(self, requests_post, utils_get_landowner):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        for x in range(1, 8):
            cat = Category(id=x, name='A' + str(x), parent=catA)
            cat.save()
        requests_post.json.return_value = {'features': []}
        utils_get_landowner.return_value = 'TEST landowner'
        ii = IssueImporter(cmd, './legacy/tests/basic.csv')
        self.assertEqual(Issue.objects.count(), 8)
    
    def test_import_csv_issues_chunks(self, requests_post, utils_get_landowner):
        """Check splitting import in chunks"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        for x in range(1, 8):
            cat = Category(id=x, name='A' + str(x), parent=catA)
            cat.save()
        requests_post.json.return_value = {'features': []}
        utils_get_landowner.return_value = 'TEST landowner'
        ii = IssueImporter(cmd, './legacy/tests/basic.csv', chunkSize=3)
        self.assertEqual(Issue.objects.count(), 8)

    def test_import_csv_categories_basic(self, requests_post, utils_get_landowner):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        ci = CategoryImporter(cmd, './legacy/tests/basic-cat.csv')
        self.assertEqual(Category.objects.count(), 11)

    def test_import_csv_categories_clean(self, requests_post, utils_get_landowner):
        """Check if clean removes existing objects"""
        cat = Category(name='Testcategory')
        cat.save()
        cmd = BaseCommand()
        cati = CategoryImporter(cmd, './legacy/tests/basic-cat.csv')
        self.assertEqual(Category.objects.count(), 11)

    def test_import_csv_comments_basic(self, requests_post, utils_get_landowner):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        requests_post.json.return_value = {'features': []}
        utils_get_landowner.return_value = 'TEST landowner'
        issue = Issue(id=1, description="test issue with defined id", position=Point(5, 23), category=catA)
        issue.save()
        issue = Issue(id=2, description="test issue with defined id", position=Point(5, 23), category=catA)
        issue.save()
        commi = CommentImporter(cmd, './legacy/tests/basic-comment.csv','./legacy/tests/basic-users-mapping.csv')
        self.assertEqual(Comment.objects.count(), 2)
    
    def test_import_csv_feedback_basic(self, requests_post, utils_get_landowner):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        catA = Category(id=0, name='Category A')
        catA.save()
        requests_post.json.return_value = {'features': []}
        utils_get_landowner.return_value = 'TEST landowner'
        issue = Issue(id=1, description="test issue with defined id", position=Point(5, 23), category=catA)
        issue.save()
        issue = Issue(id=2, description="test issue with defined id", position=Point(5, 23), category=catA)
        issue.save()
        fbi = FeedbackImporter(cmd, './legacy/tests/basic-feedback.csv')
        self.assertEqual(Feedback.objects.count(), 2)

    def test_import_csv_user_basic(self, requests_post, utils_get_landowner):
        """Check if parsing a wellformed CSV works fine"""
        cmd = BaseCommand()
        grp = Group(name='theuser')
        grp.save()
        ubi = UserImporter(cmd, './legacy/tests/basic-users-mapping.csv')
        self.assertEqual(User.objects.count(), 4)
