# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-09 06:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0040_auto_20170203_0250'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('tests', models.ManyToManyField(to='randomtest.Test')),
            ],
        ),
    ]
