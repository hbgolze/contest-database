# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-03-11 23:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0105_auto_20190311_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='contesttest',
            name='short_label',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]