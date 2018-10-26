# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-10-25 04:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_relayprob_forteam_format1_problem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('letter', models.CharField(max_length=1)),
                ('label', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterModelOptions(
            name='contestyear',
            options={'ordering': ['year']},
        ),
        migrations.AddField(
            model_name='indivprob_format1',
            name='prefix',
            field=models.CharField(default='I', max_length=16),
        ),
        migrations.AddField(
            model_name='team_format1',
            name='total_indiv_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team_format1',
            name='total_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team_format1',
            name='total_team_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team_format1',
            name='new_site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='results.Site'),
        ),
    ]
