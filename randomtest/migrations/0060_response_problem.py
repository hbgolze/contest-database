# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-19 22:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0059_solution_display_solution_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem'),
        ),
    ]