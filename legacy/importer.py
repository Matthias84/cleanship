from django.core.management.base import BaseCommand, CommandError
from common.models import Issue
from itertools import islice
import csv
import time

def import_issues(cmd, filename = 'klarschiff_vorgang.csv', SIZE_CHUNK = 500, OFFSET = 0, LIMIT = None):
		"""
		Add old issues from CSV export in n chunks and starting from offset line till limit line
		(requires existing categories)
		"""
		with open(filename) as f:
			linesFile = sum(1 for line in f)
		linesFile -= 1
		with open(filename) as csvfile:
			NESSESARY_FIELDS = ['id','beschreibung','autor_email']
			EMAIL_HIDDEN = '- bei Archivierung entfernt -'
			Issue.objects.all().delete()
			cmd.stdout.write(cmd.style.SUCCESS('Reading %s ...') % filename)
			reader = csv.DictReader(csvfile)
			if all(field in reader.fieldnames for field in NESSESARY_FIELDS):
				start_time = time.time()
				issueCount = 0
				lineCount = 0
				chunk =[]
				for row in islice(reader, OFFSET, None):
					id = row['id']
					descr = row['beschreibung']
					email = row['autor_email']
					#TODO: Add IGNORE_FIELDS (old)
					if Issue.objects.filter(id=id).exists():
						cmd.stdout.write("(skipped %s)" % id)
					else:
						if email == EMAIL_HIDDEN:
							email = None
						issueCount += 1
						issue = Issue(id=id, description = descr, authorEmail = email)
						chunk.append(issue)
					lineCount += 1
					if issueCount % SIZE_CHUNK == 0:
						perc = 100 - int(linesFile / lineCount)
						chunkId = int(issueCount / SIZE_CHUNK)
						cmd.stdout.write(cmd.style.SUCCESS("%s%% (chunk %s)" % (perc, chunkId)))
						Issue.objects.bulk_create(chunk)
						chunk = []
					if issueCount == LIMIT:   
						break;
				# submit last open chunk
				perc = 100 - int(linesFile / lineCount)
				chunkId = int(issueCount / SIZE_CHUNK)
				cmd.stdout.write(cmd.style.SUCCESS("%s%% (chunk %s)" % (perc, chunkId)))
				Issue.objects.bulk_create(chunk)
				runTime = (time.time() - start_time)
				cmd.stdout.write(cmd.style.SUCCESS('Imported %s issues (%.2f sec)') % (issueCount, runTime))
			else:
				cmd.stdout.write(cmd.style.ERROR('Error - CSV file missing fields (expexted: %s)' % NESSESARY_FIELDS))
