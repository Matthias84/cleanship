# Generated by Django 2.2.6 on 2019-11-02 18:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_issue_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 2, 18, 54, 55, 754214, tzinfo=utc)),
        ),
    ]