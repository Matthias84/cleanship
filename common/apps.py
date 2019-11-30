from django.apps import AppConfig
from django.db.models.signals import pre_save


class CommonConfig(AppConfig):
    name = 'common'
    
    def ready(self):
        """Register hooks/signals"""
        from .models import save_issue, Issue
        pre_save.connect(save_issue, sender=Issue)
