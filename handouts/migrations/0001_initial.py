# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-24 01:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('randomtest', '0061_problem_latex_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('chapter_number', models.IntegerField(default=0)),
                ('section_number', models.IntegerField(default=0)),
                ('subsection_number', models.IntegerField(default=0)),
                ('order', models.IntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Handout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('order', models.IntegerField()),
                ('top_section_number', models.IntegerField(default=0)),
                ('top_subsection_number', models.IntegerField(default=0)),
                ('document_elements', models.ManyToManyField(blank=True, to='handouts.DocumentElement')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Proof',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(max_length=20)),
                ('proof_code', models.TextField(blank=True)),
                ('proof_display', models.TextField(blank=True)),
                ('isSolution', models.BooleanField(default=0)),
                ('solution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Solution')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='SubSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='TextBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_code', models.TextField(blank=True)),
                ('text_display', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Theorem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150)),
                ('prefix', models.CharField(max_length=20)),
                ('theorem_code', models.TextField(blank=True)),
                ('theorem_display', models.TextField(blank=True)),
                ('isProblem', models.BooleanField(default=0)),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
            ],
        ),
    ]
