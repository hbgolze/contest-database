# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 07:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0008_auto_20161017_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='form',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='problem',
            name='testlabel',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]