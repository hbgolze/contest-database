# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-11 04:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0024_userunitobject_unit_object'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userproblemset',
            options={},
        ),
        migrations.AlterModelOptions(
            name='userslides',
            options={},
        ),
        migrations.AlterModelOptions(
            name='usertest',
            options={},
        ),
        migrations.RemoveField(
            model_name='userproblemset',
            name='order',
        ),
        migrations.RemoveField(
            model_name='userslides',
            name='order',
        ),
        migrations.RemoveField(
            model_name='usertest',
            name='order',
        ),
    ]
