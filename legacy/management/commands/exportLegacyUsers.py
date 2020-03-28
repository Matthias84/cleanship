from django.core.management.base import BaseCommand

from legacy.exporter import LegacyUserDetailsExporter

# TODO: Tests and try()


class Command(BaseCommand):

    help = 'Export merged Klarschiff user details from CSV export Klarschiff backend 1.9 DE'

    def handle(self, *args, **options):
        """Process CSV export DB tables of Klarschiff"""
        exporter = LegacyUserDetailsExporter(cmd=self)
