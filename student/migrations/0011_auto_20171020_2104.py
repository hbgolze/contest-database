# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-10-21 02:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_auto_20171020_2058'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproblemset',
            name='userunitobject',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.UserUnitObject'),
        ),
        migrations.AddField(
            model_name='userslides',
            name='userunitobject',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.UserUnitObject'),
        ),
    ]
