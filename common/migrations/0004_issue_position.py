# Generated by Django 2.2.6 on 2019-10-27 12:24

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_issue_authoremail'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='position',
            field=django.contrib.gis.db.models.fields.PointField(default=None, srid=25833),
            preserve_default=False,
        ),
    ]
