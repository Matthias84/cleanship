# Generated by Django 2.2.6 on 2020-03-28 10:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0025_auto_20200328_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='recipient',
            field=models.ForeignKey(help_text='Who wrote the content.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipient', to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
    ]