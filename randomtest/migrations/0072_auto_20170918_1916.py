# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-19 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0071_usertest_show_answer_marks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertest',
            name='responses',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usertest', to='randomtest.Responses'),
        ),
    ]
