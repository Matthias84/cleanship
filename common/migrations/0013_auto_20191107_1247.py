# Generated by Django 2.2.6 on 2019-11-07 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('common', '0012_issue_assigned'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='delegated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delegatedIssues', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='assigned',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignedIssues', to='auth.Group'),
        ),
    ]