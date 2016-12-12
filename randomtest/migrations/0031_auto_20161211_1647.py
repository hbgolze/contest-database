# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 22:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('randomtest', '0030_auto_20161202_1033'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_status', models.CharField(choices=[('AP', 'Approved'), ('MN', 'Approved Subject to Minor Revision'), ('MJ', 'Needs Major Revision'), ('DE', 'Propose For Deletion')], default='MJ', max_length=2)),
                ('approval_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='approvals',
            field=models.ManyToManyField(blank=True, to='randomtest.ProblemApproval'),
        ),
    ]