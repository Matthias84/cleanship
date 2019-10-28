from django.core.management.base import BaseCommand, CommandError

from legacy.importer import import_issues, import_cat

#TODO: Refactor to generic CSVKSImporter for bulk, progress, ... support
#TODO: Tests and try()

class Command(BaseCommand):
	help = 'Import Klarschiff datasets from CSV export Klarschiff backend 1.9 DE'
	

	def handle(self, *args, **options):
		"""Process CSV export DB tables of Klarschiff"""
		import_cat(self)
		import_issues(self)
