from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    pass

    def __str__(self):
        return self.email


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=500)  # BUG: Could be empty, whats the right way?
    authorEmail = models.EmailField(null=True, blank=False)
    position = models.PointField(srid=25833)  # TODO: Extract srid to settings
    category = TreeForeignKey('Category', on_delete=models.CASCADE, null=False, blank=False)
    photo = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


class Category(MPTTModel):
        name = models.CharField(max_length=50)
        parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)

        class MPTTMeta:
                order_insertion_by = ['name']

        class Meta:
                unique_together = (('id', 'name',))
                verbose_name_plural = 'categories'

        def __str__(self):
                return self.name
