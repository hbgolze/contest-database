# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-26 00:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0074_auto_20170920_1858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='handouts',
        ),
    ]