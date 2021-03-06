# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-02-07 03:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0100_auto_20180418_0256'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contest_label', models.CharField(blank=True, max_length=100)),
                ('year', models.IntegerField(default=2019)),
                ('form_letter', models.CharField(blank=True, max_length=2)),
            ],
            options={
                'ordering': ['year', 'form_letter'],
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='type',
            name='max_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='type',
            name='min_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contesttest',
            name='contest_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contests', to='randomtest.Type'),
        ),
        migrations.AddField(
            model_name='contesttest',
            name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contests', to='randomtest.Round'),
        ),
    ]
