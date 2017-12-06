# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-16 23:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0022_auto_20171116_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemobject',
            name='a_problemset',
        ),
        migrations.RemoveField(
            model_name='problemset',
            name='problem_objects',
        ),
        migrations.RemoveField(
            model_name='publishedproblemset',
            name='problem_objects',
        ),
        migrations.AddField(
            model_name='problemobject',
            name='problemset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_objects', to='teacher.ProblemSet'),
        ),
        migrations.AlterField(
            model_name='problemobject',
            name='test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_objects', to='teacher.Test'),
        ),
        migrations.AlterField(
            model_name='publishedproblemobject',
            name='problemset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_objects', to='teacher.PublishedProblemSet'),
        ),
        migrations.AlterField(
            model_name='publishedproblemobject',
            name='test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_objects', to='teacher.PublishedTest'),
        ),
    ]