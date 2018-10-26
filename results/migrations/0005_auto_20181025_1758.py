# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-10-25 22:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0004_auto_20181024_2316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indivprob_format1',
            options={'ordering': ['problem_number']},
        ),
        migrations.AlterModelOptions(
            name='relayprob_format1',
            options={'ordering': ['problem_number']},
        ),
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['letter']},
        ),
        migrations.AddField(
            model_name='indivprob_forteam_format1',
            name='problem_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='relayprob_forteam_format1',
            name='problem_number',
            field=models.IntegerField(default=0),
        ),
    ]
