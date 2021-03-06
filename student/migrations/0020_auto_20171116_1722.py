# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-16 23:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0019_usertest'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='blank_point_value',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='response',
            name='user_test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.UserTest'),
        ),
        migrations.AlterField(
            model_name='response',
            name='user_problemset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='student.UserProblemSet'),
        ),
    ]
