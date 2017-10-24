# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-26 00:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('handouts', '0008_delete_imagemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proof',
            name='solution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='handout_proof', to='randomtest.Solution'),
        ),
    ]
