from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.gis.db import models
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from mptt.models import MPTTModel, TreeForeignKey
from enum import IntEnum
import json
import logging
from .utils import reverse_geocode, get_landowner


logger = logging.getLogger(__name__)

class User(AbstractUser):

    def __str__(self):
        return self.email

class PriorityTypes(IntEnum):
    """Enum how important a issue is (e.g. danger of life)"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    # to get strings for translation
    gettext_noop("LOW")
    gettext_noop("low")
    gettext_noop("NORMAL")
    gettext_noop("normal")
    gettext_noop("HIGH")
    gettext_noop("high")

    @classmethod
    def choices(cls):
        return [(key.value, _(key.name)) for key in cls]

class StatusTypes(IntEnum):
    """Enum of current step in finding a solution to the issue"""
    SUBMITTED = 1
    WIP = 2
    SOLVED = 3
    IMPOSSIBLE = 4
    DUBLICATE = 5
    # TODO: Add unassigned / offen #12
    # TODO: Add deleted / geloescht #13
    # to get strings for translation
    gettext_noop("SUBMITTED")
    gettext_noop("submitted")
    gettext_noop("WIP")
    gettext_noop("wip")
    gettext_noop("SOLVED")
    gettext_noop("solved")
    gettext_noop("IMPOSSIBLE")
    gettext_noop("impossible")
    gettext_noop("DUBLICATE")
    gettext_noop("dublicate")
    

    @classmethod
    def choices(cls):
        return [(key.value, _(key.name)) for key in cls]

class TrustTypes(IntEnum):
    """Enum of trust level for issue authors"""
    EXTERNAL = 1
    INTERNAL = 2
    FIELDTEAM = 3

    @classmethod
    def choices(cls):
        return [(key.value, _(key.name)) for key in cls]
    
    # to get strings for translation
    gettext_noop("EXTERNAL")
    gettext_noop("external")
    gettext_noop("INTERNAL")
    gettext_noop("internal")
    gettext_noop("FIELDTEAM")
    gettext_noop("fieldteam")

def validate_in_municipality(value):
    """Check if map point is within boundary"""
    # TODO: Extract validators, switch datasource #56
    position = value
    position.transform(4326)
    logger.debug('Checking issue position ({})'.format(position))
    ds = DataSource('municipality_area.json')
    poly = ds[0].get_geoms(geos=True)[0]
    poly.srid = 4326
    logger.debug('Loaded area polygon') #TODO: provide more characteristics?
    if poly.contains(position) == False:
        logger.debug('Point ({}) not within area polygon'.format(position.coords))
        raise ValidationError(
            _('Position must be within the municipality area.'),
            code='error_bounds',
        )

def validate_is_subcategory(value):
    """Only 3rd level is a full type/main category/sub category"""
    cat = Category.objects.get(id=value)
    if cat.level < 2:
        raise ValidationError(
            _('Category must be a subcategory (3. level).'),
            code='error_cats')

def get_trust(email):
    """Detect if issue submitted via internal staff, field staff or from the public"""
    if email != None:
        if email.find('@rostock.de')>-1:
            return TrustTypes.INTERNAL
        else:
            return TrustTypes.EXTERNAL
    else:
        # Only internals can submit issues without email
        return TrustTypes.INTERNAL
    # TODO: determine FieldTeam by User groups

class Issue(models.Model):
    """A submitted ticket / service request / observation which somebody wants to be fixed / evaluated (e.g. report of waste)"""
    id = models.AutoField(primary_key=True, verbose_name=_('ID'))
    description = models.TextField(max_length=500, verbose_name=_('description'), help_text=_('Notes describing further details.'))  # BUG: Could be empty, whats the right way?
    author_email = models.EmailField(null=True, blank=False, verbose_name=_('author'), help_text=_('eMail alias of the author.'))
    author_trust = models.IntegerField(choices=TrustTypes.choices(), default=TrustTypes.EXTERNAL, verbose_name = _('trust'), help_text=_('Trust level of the author.'))
    position = models.PointField(srid=25833, verbose_name=_('position'), help_text=_('Georeference for this issue. (might be inaccurate)'), validators=[validate_in_municipality])  # TODO: Extract srid to settings
    category = TreeForeignKey('Category', on_delete=models.CASCADE, null=False, blank=False, verbose_name=_('category'), help_text=_('Multi-level selection of which kind of note this issue comes closest.'), validators=[validate_is_subcategory])
    photo = models.ImageField(upload_to='', null=True, blank=True, verbose_name=_('photo'), help_text=_('Photo that show the spot. (unprocessed, might include metadata)'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('creation date'), help_text=_('Date of submission.'))
    location = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('location'), help_text=_('Human readable description of the position.'))
    priority = models.IntegerField(choices=PriorityTypes.choices(), default=PriorityTypes.NORMAL, verbose_name = _('priority'), help_text=_('Importance of the note for responsibles.'))
    landowner = models.CharField(max_length=250, null=True, blank=True, verbose_name = _('landowner'), help_text=_('Operrator that manages the area of the position. (usually landowner, might be inaccurate)'))
    assigned = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name='assignedIssues', verbose_name=_('assigned group'), help_text=_('Responsible (internal) department, which processes the issue currently.'))
    delegated = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name='delegatedIssues', verbose_name=_('delegated group'), help_text=_('Responsible (external) organisation, which becomes involved in solving this issue.'))
    status = models.IntegerField(choices=StatusTypes.choices(), default=StatusTypes.SUBMITTED, verbose_name = _('status'), help_text=_('Stage of progress for the solution.')) # TODO: Avoid changing status backwards e.g. forms/admin
    status_text = models.TextField(max_length=1000, verbose_name=_('status text'), help_text=_('Further details explaining the progress / plans / challanges / milestones / ... .'))
    status_created_at = models.DateTimeField(default=timezone.now, verbose_name=_('status date'), help_text=_('Date of the last status change.')) # TODO: The default date needs an filter procedure to trigger only on relevant changes
    published = models.BooleanField(null=False, blank=False, default=False, verbose_name=_('published'), help_text=_('If base information are currently public. (can be altered manually and by state changes)'))
    # TODO: timestamp of last change (incl. comments / feedback / abuse?)

    class Meta:
         verbose_name = _("issue")
         verbose_name_plural = _('issues')

    def get_issue_priority_label(self):
        return PriorityTypes(self.type).name.title()
    
    def get_responsible_candidates(self):
        """Returns ordered list of groups which might be responsible to this issue"""
        # TODO: This is a dummy to be replaced with a separated app
        ls = []
        if self.category.name.find("Beschilderung") > -1:
            a66_signs = Group.objects.filter(name='a66_beschilderung').first()
            ls.append(a66_signs)
        return ls
    
    def get_position_WGS84(self):
        positionWGS84 = self.position
        positionWGS84.transform(4326)
        return positionWGS84

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        """
        Update fields (but not for bulk imports)
        """
        self.location = reverse_geocode(self.position)
        self.landowner = get_landowner(self.position)
        self.author_trust = get_trust(self.author_email)
        logger.info('Saving issue')
        super(Issue, self).save(*args, **kwargs)


class Category(MPTTModel):
    """Kind of issues which used to classify issues and find groups to get a solution"""
    name = models.CharField(max_length=50, verbose_name = 'name', help_text=_('Short label of this category.'))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True, verbose_name = 'parent', help_text='Parent category within the hierachy.')
    
    # Labels for 1st level Category types
    IDEA = 'Idee'
    PROBLEM = 'Problem'
    TIP = 'Tipp'

    class MPTTMeta:
            order_insertion_by = ['name']

    class Meta:
            unique_together = (('id', 'name',))
            verbose_name = _("category")
            verbose_name_plural = _('categories')

    def __str__(self):
            return self.name

    @classmethod
    def get_ideas_root(cls):
        """Returns 1st level root element for type 'ideas'"""
        return Category.objects.filter(name=Category.IDEA).first()

    @classmethod
    def get_problems_root(cls):
        """Returns 1st level root element for type 'problem'"""
        return Category.objects.filter(name=Category.PROBLEM).first()

    @classmethod
    def get_tips_root(cls):
        """Returns 1st level root element for type 'tips'"""
        return Category.objects.filter(name=Category.Tip).first()

class Comment(models.Model):
    """Internal comments of staff after login"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    # TODO: User needs to be model not string (if provided by #29)
    author = models.CharField(max_length=150, null=False, blank=False, verbose_name=_('author'), help_text=_('Who wrote the content.'))
    # TODO: Get number of edits + last timestamp #44
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('creation date'), help_text=_('When was the content written.'))
    content = models.TextField(max_length=500, verbose_name=_('content'), help_text=_('Text of the comment'))

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _('comments')
        ordering = ['-created_at', 'author']

    def __str__(self):
        return "{} @ {}".format(self.author, str(self.issue.id))

class Feedback(models.Model):
    """External feedback"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='feedbacks')
    # TODO: User needs to be model not string (if provided by #29)
    author_email = models.EmailField(null=True, blank=False, verbose_name=_('author'), help_text=_('eMail alias of the author (verified).'))
    # TODO: Set receiver mail alias -> which staff user was notified? #45
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('creation date'), help_text=_('When was the content written.'))
    content = models.TextField(max_length=500, verbose_name=_('content'), help_text=_('Text of the feedback'))

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _('feedback')
        ordering = ['-created_at', 'author_email']

    def __str__(self):
        return "{} to {}".format(self.author_email, str(self.issue.id))
