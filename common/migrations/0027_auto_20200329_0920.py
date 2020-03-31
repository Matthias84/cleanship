# Generated by Django 2.2.6 on 2020-03-29 07:20

import common.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0026_feedback_recipient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.IntegerField(choices=[(1, 'SUBMITTED'), (2, 'REVIEW'), (3, 'WIP'), (4, 'SOLVED'), (5, 'IMPOSSIBLE'), (6, 'DUBLICATE')], default=common.models.StatusTypes(1), help_text='Stage of progress for the solution.', verbose_name='status'),
        ),
    ]