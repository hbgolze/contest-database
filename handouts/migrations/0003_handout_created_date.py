# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-26 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('handouts', '0002_handout_top_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='handout',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
