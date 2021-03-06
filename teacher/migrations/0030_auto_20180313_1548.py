# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-03-13 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0029_auto_20171129_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='exampleproblem',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='imagemodel',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='problemobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='problemset',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='proof',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedclass',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedexampleproblem',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedimagemodel',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedproblemobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedproblemset',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedproof',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedslide',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedslidegroup',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedslideobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedtest',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedtextblock',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedtheorem',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedunit',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='publishedunitobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='slide',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='slidegroup',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='slideobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='test',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='textblock',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='theorem',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='unit',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='unitobject',
            name='version_number',
            field=models.IntegerField(default=0),
        ),
    ]
