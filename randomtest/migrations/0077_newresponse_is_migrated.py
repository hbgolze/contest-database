# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-10-31 20:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0076_auto_20170925_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='newresponse',
            name='is_migrated',
            field=models.BooleanField(default=0),
        ),
    ]
