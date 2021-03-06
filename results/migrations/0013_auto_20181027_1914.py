# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-10-28 00:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0012_team_format1_divisional_rank'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contestyear',
            options={'ordering': ['-year']},
        ),
        migrations.AddField(
            model_name='indivprob_format1',
            name='perc_correct',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='relayprob_format1',
            name='avg_points',
            field=models.FloatField(default=0),
        ),
    ]
