# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-10-10 05:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0007_auto_20171009_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exampleproblem',
            name='question_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType'),
        ),
    ]