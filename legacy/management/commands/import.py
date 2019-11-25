from django.core.management.base import BaseCommand

from legacy.importer import IssueImporter, CategoryImporter, CommentImporter, FeedbackImporter

# TODO: Tests and try()


class Command(BaseCommand):

    help = 'Import Klarschiff datasets from CSV export Klarschiff backend 1.9 DE'

    def handle(self, *args, **options):
        """Process CSV export DB tables of Klarschiff"""
        catImporter = CategoryImporter(cmd=self, csvFilename='klarschiff_kategorie.csv')
        issueimporter = IssueImporter(cmd=self, csvFilename='klarschiff_vorgang.csv', chunkSize=500)
        comImporter = CommentImporter(cmd=self, csvFilename='klarschiff_kommentar.csv', chunkSize=500)
        fbImporter = FeedbackImporter(cmd=self, csvFilename='klarschiff_lob_hinweise_kritik.csv')
