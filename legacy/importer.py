from django.utils import dateparse
from common.models import Issue, Category
from itertools import islice
import csv
import time
from datetime import timezone, timedelta

import logging

logger = logging.getLogger(__name__)


class CSVImporter:

    """
    Generic baseclass for bulk-CSV imports with statistics
    """

    NESSESARY_FIELDS = []

    def __init__(self, cmd, csvFilename, chunkSize=None, skipExisting=False, clean=True):
        # TODO: limit, offset
        self.cmd = cmd
        self.csvfilename = csvFilename
        self.chunkSize = chunkSize
        self.skipExisting = skipExisting
        self.clean = clean
        self.lines = self.countTotalLines()
        logger.debug('opening %s' % self.csvfilename)
        csvfile = open(self.csvfilename)
        self.reader = csv.DictReader(csvfile)
        cmd.stdout.write(cmd.style.SUCCESS('Reading %s ...' % self.csvfilename))
        if chunkSize is not None:
            self.cmd.stdout.write(self.cmd.style.SUCCESS("(Chunks with %s objects)" % chunkSize))
        if self.checkFields():
            if self.clean:
                self.eraseObjects()
            self.importCSV()
        else:
            cmd.stdout.write(cmd.style.ERROR('Error - CSV file missing fields (expexted: %s)' % self.NESSESARY_FIELDS))

    def countTotalLines(self):
        """get number of lines in CSV file"""
        with open(self.csvfilename) as f:
            linesFile = sum(1 for line in f)
        return linesFile

    def checkFields(self):
        """Check if all fields present in CSV header"""
        logger.debug('Check CSV header')
        return all(field in self.reader.fieldnames for field in self.NESSESARY_FIELDS)

    def importCSV(self):
        """start (possible long running) import and parsing CSV"""

        start_time = time.time()
        objCount = 0
        lineCount = 0
        chunk = []
        for row in self.reader:
            lineCount += 1
            if self.skipExisting:
                if not self.checkObjExists(row):
                    obj = self.parseRow(row)
                    objCount += 1
            else:
                obj = self.parseRow(row)
                objCount += 1
            if obj is not None:
                if self.chunkSize is None:
                    # Ignore chunks
                    obj.save()
                else:
                    # Fill chunk
                    chunk.append(obj)
                    if objCount % self.chunkSize == 0:
                        # submit if nessesary
                        perc = 100 - int(self.lines / lineCount)
                        chunkId = int(objCount / self.chunkSize)
                        self.cmd.stdout.write(self.cmd.style.SUCCESS("%s%% (chunk %s)" % (perc, chunkId)))
                        self.saveChunk(chunk)
                        chunk = []
        if self.chunkSize is not None:
            # submit last open chunk
            perc = 100 - int(self.lines / lineCount)
            chunkId = int(objCount / self.chunkSize)
            self.cmd.stdout.write(self.cmd.style.SUCCESS("%s%% (chunk %s)" % (perc, chunkId)))
            self.saveChunk(chunk)
        runTime = (time.time() - start_time)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Imported %s objects (%.2f sec)') % (objCount, runTime))

    def eraseObjects(self):
        """empty DB from objects"""
        raise NotImplementedError("Please Implement parseLine() method")

    def parseRow(self, row):
        """return DB model object from CSV fields"""
        raise NotImplementedError("Please Implement parseLine() method")

    def checkObjExists(self, row):
        """Test if model object already exists in DB"""
        raise NotImplementedError("Please Implement checkObjExists() method")

    def saveChunk(self, chunk):
        """bulk save objects"""
        raise NotImplementedError("Please Implement saveChunk() method")


class IssueImporter(CSVImporter):
    """
    Add old issues from CSV export in n chunks
    (requires existing categories)
    """

    def __init__(self, cmd, csvFilename, chunkSize=None, clean=True):
        self.NESSESARY_FIELDS = ['id', 'beschreibung', 'autor_email', 'kategorie', 'foto_gross', 'datum']
        self.EMAIL_HIDDEN = '- bei Archivierung entfernt -'
        super().__init__(cmd, csvFilename, chunkSize, clean)

    def eraseObjects(self):
        Issue.objects.all().delete()

    def parseRow(self, row):
        # TODO: Exception handling and malformed fields?
        id = row['id']
        logger.debug('parsing %s' % id)
        descr = row['beschreibung']
        email = row['autor_email']
        positionEwkb = row['ovi']
        categoryId = row['kategorie']
        photoFilename = row['foto_gross']
        created = row['datum']
        if email == self.EMAIL_HIDDEN:
            email = None
        cat = Category.objects.get(id=categoryId)
        if cat is None:
            self.cmd.stdout.write(self.cmd.style.ERROR('Error - No category found (Issue %s, Cat.Id. %s)' % (id, categoryId)))
        if photoFilename == "":
            photoFilename = None
        created = dateparse.parse_datetime(created)
        created=created.replace(tzinfo=timezone(timedelta(hours=1)))
        issue = Issue(id=id, description=descr, authorEmail=email, position=positionEwkb, category=cat, photo=photoFilename, created_at=created)
        return issue

    def checkObjExists(self, row):
        id = row['id']
        if Issue.objects.filter(id=id).exists():
            self.cmd.stdout.write("(skipping %s)" % id)
            return True
        else:
            return False

    def saveChunk(self, chunk):
        Issue.objects.bulk_create(chunk)


class CategoryImporter(CSVImporter):
    """
    Import old categories from CSV export
    """

    def __init__(self, cmd, csvFilename, chunkSize=None, skipExisting=False, clean=True):
        self.NESSESARY_FIELDS = ['id', 'name', 'typ', 'parent']
        super().__init__(cmd, csvFilename, chunkSize, skipExisting, clean)

    def eraseObjects(self):
        Category.objects.all().delete()
        problem = Category(id=200, name="Problem")
        problem.save()
        idea = Category(id=201, name="Idee")
        idea.save()
        tip = Category(id=202, name="Tipp")
        tip.save()
        self.typeMap = {"problem": problem, "idee": idea, "tipp": tip}
        # TODO: Set mapping also if no clean run

    def parseRow(self, row):
        id = row['id']
        name = row['name']
        typeClass = row['typ']
        parent_id = row['parent']
        if parent_id == '':
            # a Maincategory
            parent = self.typeMap[typeClass]
            cat = Category(id=id, name=name, parent=parent)
        else:
            # a Subcategory
            parent = Category.objects.get(id=parent_id)
            cat = Category(id=id, name=name, parent=parent)
        cat.save()
    # TODO: manager for bulk update rebuild()

