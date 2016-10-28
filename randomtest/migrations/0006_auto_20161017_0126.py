# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-17 06:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0005_remove_test_num_problems'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solution_text', models.TextField()),
                ('tags', models.ManyToManyField(blank=True, to='randomtest.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(blank=True, to='randomtest.Tag'),
        ),
        migrations.AddField(
            model_name='problem',
            name='question_type',
            field=models.ManyToManyField(blank=True, to='randomtest.QuestionType'),
        ),
        migrations.AddField(
            model_name='problem',
            name='solutions',
            field=models.ManyToManyField(blank=True, to='randomtest.Solution'),
        ),
    ]