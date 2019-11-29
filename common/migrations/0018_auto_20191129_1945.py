# Generated by Django 2.2.6 on 2019-11-29 18:45

import common.models
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_auto_20191124_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='assigned',
            field=models.ForeignKey(blank=True, help_text='Responsible (internal) department, which processes the issue currently.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignedIssues', to='auth.Group', verbose_name='assigned group'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='category',
            field=mptt.fields.TreeForeignKey(help_text='Multi-level selection of which kind of note this issue comes closest.', on_delete=django.db.models.deletion.CASCADE, to='common.Category', validators=[common.models.validate_is_subcategory], verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='delegated',
            field=models.ForeignKey(blank=True, help_text='Responsible (external) organisation, which becomes involved in solving this issue.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delegatedIssues', to='auth.Group', verbose_name='delegated group'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='landowner',
            field=models.CharField(blank=True, help_text='Operrator that manages the area of the position. (usually landowner, might be inaccurate)', max_length=250, null=True, verbose_name='landowner'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='location',
            field=models.CharField(blank=True, help_text='Human readable description of the position.', max_length=150, null=True, verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='position',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Georeference for this issue. (might be inaccurate)', srid=25833, validators=[common.models.validate_in_municipality], verbose_name='position'),
        ),
    ]
