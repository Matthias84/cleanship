from django.test import TestCase
from django.core.management.base import BaseCommand

from legacy.exporter import LegacyUserDetailsExporter

class ExportTests(TestCase):
    def test_export_legacy_users(self):
        """Check if CSV parsing and merging of old users work fine"""
        cmd = BaseCommand()
        lude = LegacyUserDetailsExporter(cmd, csvFilenameIssues='./legacy/tests/basic.csv', csvFilenameFeedback='./legacy/tests/basic-feedback.csv', csvFilenameUsers='./legacy/tests/basic-users.csv', filenameOutput='./legacy/tests/test-users.csv')
        lines = self._count_lines('./legacy/tests/test-users.csv')
        self.assertEqual(lines, 5+1+4+3)
    
    def _count_lines(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1
