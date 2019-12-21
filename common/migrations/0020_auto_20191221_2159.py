# Generated by Django 2.2.6 on 2019-12-21 20:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0019_issue_authortrust'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='status_created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Date of the last status change.', verbose_name='status date'),
        ),
        migrations.AddField(
            model_name='issue',
            name='status_text',
            field=models.TextField(default='', help_text='Further details explaining the progress / plans / challanges / milestones / ... .', max_length=1000, verbose_name='status text'),
            preserve_default=False,
        ),
    ]
