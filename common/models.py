from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.gis.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from enum import IntEnum


class User(AbstractUser):
    pass

    def __str__(self):
        return self.email

class PriorityTypes(IntEnum):
  LOW = 1
  NORMAL = 2
  HIGH = 3
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=500, help_text='Notes describing further details.')  # BUG: Could be empty, whats the right way?
    authorEmail = models.EmailField(null=True, blank=False, help_text='eMail alias of the author.')
    position = models.PointField(srid=25833, help_text='Georeference for this issue. (might be inaccurate)')  # TODO: Extract srid to settings
    category = TreeForeignKey('Category', on_delete=models.CASCADE, null=False, blank=False, help_text='Multi-level selection of which kind of note this issue comes closest.')
    photo = models.ImageField(null=True, blank=True, help_text='Photo that show the spot. (unprocessed, might include metadata)')
    created_at = models.DateTimeField(default=timezone.now, help_text='Date of submission.')
    location = models.CharField(max_length=150, null=True, help_text='Human readable description of the position.')
    priority = models.IntegerField(choices=PriorityTypes.choices(), default=PriorityTypes.NORMAL, help_text='Importance of the note for responsibles.')
    landowner = models.CharField(max_length=250, null=True, help_text='Operrator that manages the area of the position. (usually landowner, might be inaccurate)')
    assigned = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL, related_name='assignedIssues', help_text='Responsible (internal) department, which processes the issue currently.')
    delegated = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL, related_name='delegatedIssues', help_text='Responsible (external) organisation, which becomes involved in solving this issue.')
    
    def get_issue_priority_label(self):
        return PriorityTypes(self.type).name.title()


class Category(MPTTModel):
        name = models.CharField(max_length=50, help_text='Short label of this category.')
        parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True, help_text='Parent category within the hierachy.')

        class MPTTMeta:
                order_insertion_by = ['name']

        class Meta:
                unique_together = (('id', 'name',))
                verbose_name_plural = 'categories'

        def __str__(self):
                return self.name
