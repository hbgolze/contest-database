# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-26 18:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handouts', '0003_handout_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='theorem',
            name='theorem_number',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='handout',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]