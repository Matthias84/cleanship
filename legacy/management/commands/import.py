from django.core.management.base import BaseCommand

from legacy.importer import IssueImporter, CategoryImporter, CommentImporter, FeedbackImporter, UserImporter

# TODO: Tests and try()

class Command(BaseCommand):

    help = 'Import Klarschiff datasets from CSV export Klarschiff backend 1.9 DE'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Import Klarschiff categories',
        )
        parser.add_argument(
            '--issues',
            action='store_true',
            help='Import Klarschiff issues and groups',
        )
        parser.add_argument(
            '--users',
            action='store_true',
            help='Import Klarschiff users',
        )
        parser.add_argument(
            '--comments',
            action='store_true',
            help='Import Klarschiff comments',
        )
        parser.add_argument(
            '--feedbacks',
            action='store_true',
            help='Import Klarschiff comments',
        )
        

    def handle(self, *args, **options):
        """Process CSV export DB tables of Klarschiff"""
        
        # nothing set? -> make all run in the right order
        if not (options['users'] and options['categories'] and options['issues'] and options['comments'] and options['feedbacks']):
            options['users'] = True
            options['categories'] = True
            options['issues'] = True
            options['comments'] = True
            options['feedbacks'] = True
        
        if options['users']:
            userImporter = UserImporter(cmd=self, csvFilename='users.csv')
        if options['categories']:
            catImporter = CategoryImporter(cmd=self, csvFilename='klarschiff_kategorie.csv')
        if options['issues']:
            issueimporter = IssueImporter(cmd=self, csvFilename='klarschiff_vorgang.csv', chunkSize=500)
        if options['comments']:
            comImporter = CommentImporter(cmd=self, csvFilename='klarschiff_kommentar.csv', chunkSize=500)
        if options['feedbacks']:
            fbImporter = FeedbackImporter(cmd=self, csvFilename='klarschiff_lob_hinweise_kritik.csv')
        
