# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-12-01 18:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0079_auto_20171120_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='parent_problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem'),
        ),
    ]
