from django.core.management.base import BaseCommand, CommandError
from common.models import Issue, Category
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
			NESSESARY_FIELDS = ['id','beschreibung','autor_email', 'kategorie', 'foto_gross']
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
					positionEwkb = row['ovi']
					categoryId = row['kategorie']
					photoFilename = row['foto_gross']
					#TODO: Add IGNORE_FIELDS (old)
					if Issue.objects.filter(id=id).exists():
						cmd.stdout.write("(skipped %s)" % id)
					else:
						if email == EMAIL_HIDDEN:
							email = None
						cat = Category.objects.get(id=categoryId)
						if cat == None:
							cmd.stdout.write(cmd.style.ERROR('Error - No category found (Issue %s, Cat.Id. %s)' % (id, categoryId)))
						if photoFilename == "":
							photoFilename = None
						issueCount += 1
						issue = Issue(id=id, description = descr, authorEmail = email, position = positionEwkb, category = cat, photo = photoFilename)
						chunk.append(issue)
					lineCount += 1
					if issueCount % SIZE_CHUNK == 0:
						# submit current chunk
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

def import_cat(cmd, filename = 'klarschiff_kategorie.csv'):
		"""Import old categories from CSV export"""
		with open(filename) as f:
			linesFile = sum(1 for line in f)
		with open(filename) as csvfile:
			NESSESARY_FIELDS = ['id','name', 'typ', 'parent']
			Category.objects.all().delete()
			cmd.stdout.write(cmd.style.SUCCESS('Reading %s ...' % filename))
			reader = csv.DictReader(csvfile)
			if all(field in reader.fieldnames for field in NESSESARY_FIELDS):
				# Create root type categories (higher ids after reserved legacy block)
				problem = Category(id=200, name="Problem")
				problem.save();
				idea = Category(id=201, name="Idee")
				idea.save();
				tip = Category(id=202, name="Tipp")
				tip.save();
				typeMap = {"problem": problem, "idee": idea, "tipp": tip}
				for row in reader:
					id = row['id']
					name = row['name']
					typeClass = row['typ']
					parent_id = row['parent']
					if parent_id == '':
						# a Maincategory
						parent = typeMap[typeClass]
						cat = Category(id=id, name = name, parent = parent)
					else:
						# a Subcategory
						parent = Category.objects.get(id=parent_id)
						cat = Category(id=id, name = name, parent = parent)
					cat.save()
				#TODO: manager for bulk update rebuild()
