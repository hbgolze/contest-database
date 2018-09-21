# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-16 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0097_auto_20180305_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=200)),
                ('author', models.CharField(default='', max_length=200)),
                ('year', models.CharField(blank=True, default='', max_length=4)),
                ('contest_name', models.CharField(default='', max_length=30)),
                ('contest_short_name', models.CharField(default='', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='type',
            name='is_sourced',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='source',
            name='source_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.SourceType'),
        ),
        migrations.AddField(
            model_name='problem',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Source'),
        ),
    ]