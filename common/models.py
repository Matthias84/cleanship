from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass
    
    def __str__(self):
        return self.email


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=500) #BUG: Could be empty, whats the right way?
    authorEmail = models.EmailField(null=True, blank=False)
