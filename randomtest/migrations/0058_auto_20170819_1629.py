# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-19 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0057_auto_20170819_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='display_mc_problem_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='problem',
            name='display_problem_text',
            field=models.TextField(blank=True),
        ),
    ]
