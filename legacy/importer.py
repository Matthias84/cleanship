from django.contrib.auth.models import Group
from django.utils import dateparse
from common.models import Issue, Category, PriorityTypes, StatusTypes, TrustTypes, Comment, Feedback, User
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
        logger.debug('opening {}'.format(self.csvfilename))
        csvfile = open(self.csvfilename)
        self.reader = csv.DictReader(csvfile)
        cmd.stdout.write(cmd.style.SUCCESS('Reading {} ...'.format(self.csvfilename)))
        if chunkSize is not None:
            self.cmd.stdout.write(self.cmd.style.SUCCESS("(Chunks with {} objects)".format(chunkSize)))
        if self.checkFields():
            if self.clean:
                self.eraseObjects()
            self.importCSV()
        else:
            cmd.stdout.write(cmd.style.ERROR('Error - CSV file missing fields (expexted: {})'.format(self.NESSESARY_FIELDS)))

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
                        self.cmd.stdout.write(self.cmd.style.SUCCESS("{}% (chunk {})".format(perc, chunkId)))
                        self.saveChunk(chunk)
                        chunk = []
        if self.chunkSize is not None:
            # submit last open chunk
            perc = 100 - int(self.lines / lineCount)
            chunkId = int(objCount / self.chunkSize)
            self.cmd.stdout.write(self.cmd.style.SUCCESS("{}% (chunk {})".format(perc, chunkId)))
            self.saveChunk(chunk)
        runTime = (time.time() - start_time)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Imported {0} objects ({1:.2f} sec)').format(objCount, runTime))

    def eraseObjects(self):
        """empty DB from objects"""
        raise NotImplementedError("Please Implement eraseObjects() method")

    def parseRow(self, row):
        """return DB model object from CSV fields"""
        raise NotImplementedError("Please Implement parseRow() method")

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
        self.NESSESARY_FIELDS = ['id', 'beschreibung', 'autor_email', 'kategorie', 'foto_gross', 'datum', 'prioritaet', 'flurstueckseigentum', 'status', 'archiviert', 'foto_freigabe_status', 'beschreibung_freigabe_status', 'trust', 'status_kommentar', 'status_datum']
        self.EMAIL_HIDDEN = '- bei Archivierung entfernt -'
        self.LOCATION_UNKOWN = 'nicht zuordenbar'
        self.MAP_PRIORITY = {'mittel': PriorityTypes.NORMAL, 'niedrig': PriorityTypes.LOW, 'hoch': PriorityTypes.HIGH}
        self.ASSIGNED_OK = 'akzeptiert'
        self.MAP_STATUS = {'gemeldet': StatusTypes.SUBMITTED, 'offen': StatusTypes.REVIEW, 'inBearbeitung': StatusTypes.WIP, 'geloest': StatusTypes.SOLVED, 'nichtLoesbar': StatusTypes.IMPOSSIBLE, 'duplikat': StatusTypes.DUBLICATE, 'geloescht': StatusTypes.DUBLICATE}
        self.MAP_ARCHIVE = {'t': True, 'f': False, '': False}
        self.MAP_PUBLIC = {'extern': True, 'intern': False, 'geloescht': False} # TODO: Process deleted photo #48
        self.MAP_TRUST = {'0': TrustTypes.EXTERNAL, '1': TrustTypes.INTERNAL, '2': TrustTypes.FIELDTEAM}
        super().__init__(cmd, csvFilename, chunkSize, clean)

    def eraseObjects(self):
        Issue.objects.all().delete()

    def parseRow(self, row):
        # TODO: Exception handling and malformed fields?
        id = row['id']
        logger.debug('parsing {}'.format(id))
        descr = row['beschreibung']
        email = row['autor_email']
        trust = row['trust']
        positionEwkb = row['ovi']
        categoryId = row['kategorie']
        photoFilename = row['foto_gross']
        created = row['datum']
        location = row['adresse']
        priority = row['prioritaet']
        landowner = row['flurstueckseigentum']
        assigned = row['zustaendigkeit']
        assigned_state = row['zustaendigkeit_status']
        delegated = row['delegiert_an']
        status = row['status']
        status_text = row['status_kommentar']
        status_created_at = row['status_datum']
        archive = row['archiviert']
        public_photo = row['foto_freigabe_status']
        public_descr = row['beschreibung_freigabe_status']
        if email == self.EMAIL_HIDDEN:
            email = None
        trust = self.MAP_TRUST[trust]
        cat = Category.objects.get(id=categoryId)
        if cat is None:
            self.cmd.stdout.write(self.cmd.style.ERROR('Error - No category found (Issue {}, Cat.Id. {})'.format(id, categoryId)))
        if photoFilename == '':
            photoFilename = None
        created = dateparse.parse_datetime(created)
        created=created.replace(tzinfo=timezone(timedelta(hours=1)))
        if location == self.LOCATION_UNKOWN:
            location = None
        priority = self.MAP_PRIORITY[priority]
        if assigned_state == self.ASSIGNED_OK:
            group_assigned, was_created = Group.objects.get_or_create(name=assigned)
        else:
            group_assigned = None
        if delegated == '':
            group_delegated = None
        else:
            group_delegated, was_created = Group.objects.get_or_create(name=delegated)
        status = self.MAP_STATUS[status]
        status_created_at = dateparse.parse_datetime(status_created_at)
        status_created_at = status_created_at.replace(tzinfo=timezone(timedelta(hours=1)))
        published = self.MAP_ARCHIVE[archive]
        if published == True:
            # Check if all content is published
            if self.MAP_PUBLIC[public_photo] and self.MAP_PUBLIC[public_descr]:
                published = True
            else:
                published = False
        issue = Issue(id=id, description=descr, author_email=email, author_trust=trust, position=positionEwkb, category=cat, photo=photoFilename, created_at=created, location=location, priority=priority, landowner=landowner, assigned=group_assigned, delegated=group_delegated, status=status, status_text=status_text, status_created_at=status_created_at, published=published)
        return issue

    def checkObjExists(self, row):
        id = row['id']
        if Issue.objects.filter(id=id).exists():
            self.cmd.stdout.write("(skipping {})".format(id))
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
        problem = Category(id=200, name=Category.PROBLEM)
        problem.save()
        idea = Category(id=201, name=Category.IDEA)
        idea.save()
        tip = Category(id=202, name=Category.TIP)
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

class CommentImporter(CSVImporter):
    """
    Add old internal issue comments from CSV export
    (requires existing issues, users)
    """

    def __init__(self, cmd, csvFilename, chunkSize=None, skipExisting=False, clean=True):
        self.NESSESARY_FIELDS = ['datum', 'nutzer', 'text', 'vorgang']
        self.cmd = cmd
        self.author2user = self.loadUserMapping()
        super().__init__(cmd, csvFilename, chunkSize, skipExisting, clean)

    def eraseObjects(self):
        Comment.objects.all().delete()

    def parseRow(self, row):
        id = row['id']
        created_at = row['datum']
        authorstring = row['nutzer']
        content = row['text']
        issue_id = row['vorgang']
        created_at = dateparse.parse_datetime(created_at)
        created_at=created_at.replace(tzinfo=timezone(timedelta(hours=1)))
        try:
            #try to map legacy Klarschiff userstring to new user ID
            authorstring = authorstring.strip()
            username = self.author2user[authorstring].lower()
            user = User.objects.get(username=username)
        except KeyError:
            self.cmd.stdout.write(self.cmd.style.WARNING('Warning - No mapping for author "{}". Comment #{}'.format(authorstring, id)))
            user = None
        except User.DoesNotExist:
            self.cmd.stdout.write(self.cmd.style.WARNING('Warning - Wrong mapping for author "{}" -> {}. Comment #{}'.format(authorstring, username, id)))
            user = None
        issue = Issue.objects.get(id=issue_id)
        comment = Comment(created_at=created_at, author=user, content=content, issue=issue)
        comment.save()
    
    def saveChunk(self, chunk):
        Comment.objects.bulk_create(chunk)
    
    def loadUserMapping(self, csvfilename='users.csv'):
        """Open CSV with mapping and return dict fullname -> userid"""
        logger.debug('opening {}'.format(csvfilename))
        csvfile = open(csvfilename)
        reader = csv.DictReader(csvfile)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Reading {} ...'.format(csvfilename)))
        fullnames=set()
        old2new = {}
        for row in reader:
            old2new[row['old_fullname']] = row['username']
        csvfile.close()
        return old2new

class FeedbackImporter(CSVImporter):
    """
    Add old external issue feedback from CSV export
    (requires existing issues, users)
    """

    def __init__(self, cmd, csvFilename, chunkSize=None, skipExisting=False, clean=True):
        self.NESSESARY_FIELDS = ['datum', 'autor_email', 'freitext', 'vorgang', 'empfaenger_email']
        self.cmd = cmd
        self.email2user = self.getUserMapping()
        super().__init__(cmd, csvFilename, chunkSize, skipExisting, clean)

    def eraseObjects(self):
        Feedback.objects.all().delete()

    def parseRow(self, row):
        id = row['id']
        created_at = row['datum']
        authorEmail = row['autor_email']
        content = row['freitext']
        issue_id = row['vorgang']
        recipientEmail = row['empfaenger_email']
        created_at = dateparse.parse_datetime(created_at)
        created_at=created_at.replace(tzinfo=timezone(timedelta(hours=1)))
        try:
            recipientEmail = recipientEmail.lower()
            recipientEmail = recipientEmail.strip()
            if not recipientEmail or recipientEmail == '':
                self.cmd.stdout.write(self.cmd.style.WARNING('Warning - No recipent "{}". Feedback #{}'.format(recipientEmail, id)))
                user = None
            else:
                if recipientEmail.find(',') > -1:
                    self.cmd.stdout.write(self.cmd.style.WARNING('Warning - Multiple recipents, using only first one "{}". Feedback #{}'.format(recipientEmail, id)))
                    recipientEmail = recipientEmail.split(',')[0]
                username = self.email2user[recipientEmail]
                user = User.objects.get(username=username)
        except KeyError:
            self.cmd.stdout.write(self.cmd.style.WARNING('Warning - No mapping for recipient "{}". Feedback #{}'.format(recipientEmail, id)))
            user = None
        issue = Issue.objects.get(id=issue_id)
        feedback = Feedback(created_at=created_at, author_email=authorEmail, recipient=user, content=content, issue=issue)
        feedback.save()
    
    def saveChunk(self, chunk):
        Feedback.objects.bulk_create(chunk)
    
    def getUserMapping(self):
        """return dict email -> userid"""
        mail2user = {}
        users = User.objects.all()
        for user in users:
            mail2user[user.email] = user.username
        return mail2user
            
        
            
class UserImporter(CSVImporter):
    """
    Create users from manually composed CSV mapping file
    (requires existing groups)
    """

    def __init__(self, cmd, csvFilename, chunkSize=None, skipExisting=False, clean=True):
        self.NESSESARY_FIELDS = ['old_fullname', 'email', 'firstname', 'lastname','username', 'group']
        super().__init__(cmd, csvFilename, chunkSize, skipExisting, clean)

    def eraseObjects(self):
        pass
        #User.objects.all().delete()

    def parseRow(self, row):
        username = row['username'].lower()
        email = row['email'].lower()
        firstname = row['firstname']
        lastname = row['lastname']
        groupname = row['group']
        user, created = User.objects.get_or_create(username=username, email=email, first_name=firstname, last_name=lastname, password='')
        # assign group
        if groupname:
            group = Group.objects.get(name=groupname)
            group.user_set.add(user)
            group.save()

    def saveChunk(self, chunk):
        User.objects.bulk_create(chunk)
