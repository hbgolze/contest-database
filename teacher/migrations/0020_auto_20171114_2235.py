# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-15 04:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0019_auto_20171114_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemset',
            name='time_limit',
        ),
        migrations.RemoveField(
            model_name='publishedproblemset',
            name='time_limit',
        ),
    ]