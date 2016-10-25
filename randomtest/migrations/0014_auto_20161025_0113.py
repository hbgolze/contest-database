# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 06:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0013_auto_20161022_0316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dropboxurl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='questiontype',
            name='question_type',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='tests',
            field=models.ManyToManyField(blank=True, to='randomtest.Test'),
        ),
    ]
