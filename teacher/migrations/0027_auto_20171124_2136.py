# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-25 03:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0026_auto_20171124_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exampleproblem',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SlideObject'),
        ),
        migrations.AlterField(
            model_name='imagemodel',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SlideObject'),
        ),
        migrations.AlterField(
            model_name='proof',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SlideObject'),
        ),
        migrations.AlterField(
            model_name='publishedexampleproblem',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedSlideObject'),
        ),
        migrations.AlterField(
            model_name='publishedimagemodel',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedSlideObject'),
        ),
        migrations.AlterField(
            model_name='publishedproof',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedSlideObject'),
        ),
        migrations.AlterField(
            model_name='publishedtextblock',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedSlideObject'),
        ),
        migrations.AlterField(
            model_name='publishedtheorem',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedSlideObject'),
        ),
        migrations.AlterField(
            model_name='textblock',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SlideObject'),
        ),
        migrations.AlterField(
            model_name='theorem',
            name='slide_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SlideObject'),
        ),
    ]
