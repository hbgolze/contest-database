# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0007_auto_20161017_0256'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='problem_label',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='solution',
            name='solution_number',
            field=models.IntegerField(default=1),
        ),
    ]
