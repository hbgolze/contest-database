# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-03-10 23:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0101_auto_20190206_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemGroupObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
                ('problemgroup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_objects', to='randomtest.ProblemGroup')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
