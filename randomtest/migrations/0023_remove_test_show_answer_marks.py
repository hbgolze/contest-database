# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-08 20:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0022_auto_20161108_1410'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='show_answer_marks',
        ),
    ]