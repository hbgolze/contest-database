# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-15 04:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('randomtest', '0078_userprofile_time_zone'),
        ('teacher', '0018_auto_20171113_1649'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishedTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('default_point_value', models.IntegerField(default=1)),
                ('default_blank_value', models.FloatField(default=0)),
                ('total_points', models.IntegerField(default=0)),
                ('num_problems', models.IntegerField(default=0)),
                ('due_date', models.DateTimeField(null=True)),
                ('time_limit', models.TimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublishedTestProblemObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('point_value', models.IntegerField(default=1)),
                ('blank_point_value', models.FloatField(default=0)),
                ('problem_code', models.TextField(blank=True)),
                ('problem_display', models.TextField(blank=True)),
                ('isProblem', models.BooleanField(default=0)),
                ('mc_answer', models.CharField(blank=True, max_length=1)),
                ('sa_answer', models.CharField(blank=True, max_length=20)),
                ('answer_A', models.CharField(blank=True, max_length=500)),
                ('answer_B', models.CharField(blank=True, max_length=500)),
                ('answer_C', models.CharField(blank=True, max_length=500)),
                ('answer_D', models.CharField(blank=True, max_length=500)),
                ('answer_E', models.CharField(blank=True, max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='published_test_problem_object', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('default_point_value', models.IntegerField(default=1)),
                ('default_blank_value', models.FloatField(default=0)),
                ('total_points', models.IntegerField(default=0)),
                ('num_problems', models.IntegerField(default=0)),
                ('due_date', models.DateTimeField(null=True)),
                ('time_limit', models.TimeField(null=True)),
                ('unit_object', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.UnitObject')),
            ],
        ),
        migrations.CreateModel(
            name='TestProblemObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('point_value', models.IntegerField(default=1)),
                ('blank_point_value', models.FloatField(default=0)),
                ('problem_code', models.TextField(blank=True)),
                ('problem_display', models.TextField(blank=True)),
                ('isProblem', models.BooleanField(default=0)),
                ('mc_answer', models.CharField(blank=True, max_length=1)),
                ('sa_answer', models.CharField(blank=True, max_length=20)),
                ('answer_A', models.CharField(blank=True, max_length=500)),
                ('answer_B', models.CharField(blank=True, max_length=500)),
                ('answer_C', models.CharField(blank=True, max_length=500)),
                ('answer_D', models.CharField(blank=True, max_length=500)),
                ('answer_E', models.CharField(blank=True, max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_problem_object', to=settings.AUTH_USER_MODEL)),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
                ('question_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType')),
                ('test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_problem_objects', to='teacher.Test')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='publishedtestproblemobject',
            name='parent_testproblemobject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.TestProblemObject'),
        ),
        migrations.AddField(
            model_name='publishedtestproblemobject',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem'),
        ),
        migrations.AddField(
            model_name='publishedtestproblemobject',
            name='published_test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_problem_objects', to='teacher.PublishedTest'),
        ),
        migrations.AddField(
            model_name='publishedtestproblemobject',
            name='question_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType'),
        ),
        migrations.AddField(
            model_name='publishedtest',
            name='parent_test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.Test'),
        ),
        migrations.AddField(
            model_name='publishedtest',
            name='unit_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedUnitObject'),
        ),
    ]