# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-29 21:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0062_userprofile_handouts'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProofResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proof', models.TextField(blank=True)),
                ('problem_label', models.CharField(max_length=20)),
                ('modified_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('points_awarded', models.IntegerField(default=0)),
                ('attempted', models.BooleanField(default=0)),
                ('is_graded', models.BooleanField(default=0)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('allowed_types', models.ManyToManyField(blank=True, to='randomtest.Type')),
            ],
        ),
        migrations.AddField(
            model_name='sortableproblem',
            name='point_value',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_type_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='randomtest.UserType'),
        ),
    ]