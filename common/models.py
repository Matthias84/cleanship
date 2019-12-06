from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.gis.db import models
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from enum import IntEnum
import json
from .utils import reverse_geocode, get_landowner


class User(AbstractUser):

    def __str__(self):
        return self.email

class PriorityTypes(IntEnum):
    """Enum how important a issue is (e.g. danger of life)"""
    LOW = 1
    NORMAL = 2
    HIGH = 3

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

    @classmethod
    def choices(cls):
        return [(key.value, _(key.name)) for key in cls]

def validate_in_municipality(value):
    """Check if map point is within boundary"""
    # TODO: Extract validators, switch datasource #56
    position = value
    position.transform(4326)
    ds = DataSource('municipality_area.json')
    poly = ds[0].get_geoms(geos=True)[0]
    poly.srid = 4326
    if poly.contains(position) == False:
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

def save_issue(sender, instance, **kwargs):
    """
    Signal handler to update location string
    (see geocodr service https://geo.sv.rostock.de/geocodr.html
    """
    instance.location = reverse_geocode(instance.position)
    instance.landowner = get_landowner(instance.position)

class Issue(models.Model):
    """A submitted ticket / service request / observation which somebody wants to be fixed / evaluated (e.g. report of waste)"""
    id = models.AutoField(primary_key=True, verbose_name=_('ID'))
    description = models.TextField(max_length=500, verbose_name=_('description'), help_text=_('Notes describing further details.'))  # BUG: Could be empty, whats the right way?
    authorEmail = models.EmailField(null=True, blank=False, verbose_name=_('author'), help_text=_('eMail alias of the author.'))
    position = models.PointField(srid=25833, verbose_name=_('position'), help_text=_('Georeference for this issue. (might be inaccurate)'), validators=[validate_in_municipality])  # TODO: Extract srid to settings
    category = TreeForeignKey('Category', on_delete=models.CASCADE, null=False, blank=False, verbose_name=_('category'), help_text=_('Multi-level selection of which kind of note this issue comes closest.'), validators=[validate_is_subcategory])
    photo = models.ImageField(null=True, blank=True, verbose_name=_('photo'), help_text=_('Photo that show the spot. (unprocessed, might include metadata)'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('creation date'), help_text=_('Date of submission.'))
    location = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('location'), help_text=_('Human readable description of the position.'))
    priority = models.IntegerField(choices=PriorityTypes.choices(), default=PriorityTypes.NORMAL, verbose_name = _('priority'), help_text=_('Importance of the note for responsibles.'))
    landowner = models.CharField(max_length=250, null=True, blank=True, verbose_name = _('landowner'), help_text=_('Operrator that manages the area of the position. (usually landowner, might be inaccurate)'))
    assigned = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name='assignedIssues', verbose_name=_('assigned group'), help_text=_('Responsible (internal) department, which processes the issue currently.'))
    delegated = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, related_name='delegatedIssues', verbose_name=_('delegated group'), help_text=_('Responsible (external) organisation, which becomes involved in solving this issue.'))
    status = models.IntegerField(choices=StatusTypes.choices(), default=StatusTypes.SUBMITTED, verbose_name = _('status'), help_text=_('Stage of progress for the solution.'))
    published = models.BooleanField(null=False, blank=False, default=False, verbose_name=_('published'), help_text=_('If base information are currently public. (can be altered manually and by state changes)'))
    
    def get_issue_priority_label(self):
        return PriorityTypes(self.type).name.title()

    class Meta:
         verbose_name = _("issue")
         verbose_name_plural = _('issues')

    def __str__(self):
        return str(self.id)


class Category(MPTTModel):
    """Kind of issues which used to classify issues and find groups to get a solution"""
    name = models.CharField(max_length=50, verbose_name = 'name', help_text=_('Short label of this category.'))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True, verbose_name = 'parent', help_text='Parent category within the hierachy.')

    class MPTTMeta:
            order_insertion_by = ['name']

    class Meta:
            unique_together = (('id', 'name',))
            verbose_name = _("category")
            verbose_name_plural = _('categories')

    def __str__(self):
            return self.name

class Comment(models.Model):
    """Internal comments of staff after login"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
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
        return "%s @ %s" % (self.author, str(self.issue.id))

class Feedback(models.Model):
    """External feedback"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    # TODO: User needs to be model not string (if provided by #29)
    authorEmail = models.EmailField(null=True, blank=False, verbose_name=_('author'), help_text=_('eMail alias of the author (verified).'))
    # TODO: Set receiver mail alias -> which staff user was notified? #45
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('creation date'), help_text=_('When was the content written.'))
    content = models.TextField(max_length=500, verbose_name=_('content'), help_text=_('Text of the feedback'))

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _('feedback')
        ordering = ['-created_at', 'authorEmail']

    def __str__(self):
        return "%s to %s" % (self.authorEmail, str(self.issue.id))
