# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-02-25 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0094_auto_20180224_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='type',
            name='allow_form_letter',
            field=models.BooleanField(default=0),
        ),
    ]