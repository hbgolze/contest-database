# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-11 03:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0031_auto_20180313_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publishedunit',
            options={'ordering': ['order']},
        ),
    ]