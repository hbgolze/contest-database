# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-28 08:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('randomtest', '0037_problem_top_solution_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='students', to=settings.AUTH_USER_MODEL),
        ),
    ]
