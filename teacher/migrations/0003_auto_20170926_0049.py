# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-26 05:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_auto_20170926_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemobject',
            name='question_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType'),
        ),
    ]
