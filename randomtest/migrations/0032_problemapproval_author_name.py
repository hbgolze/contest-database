# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 23:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0031_auto_20161211_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemapproval',
            name='author_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
