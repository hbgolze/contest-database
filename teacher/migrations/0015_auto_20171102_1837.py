# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-11-02 23:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0077_newresponse_is_migrated'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teacher', '0014_auto_20171101_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishedExampleProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150)),
                ('prefix', models.CharField(default='', max_length=20)),
                ('problem_code', models.TextField(blank=True)),
                ('problem_display', models.TextField(blank=True)),
                ('isProblem', models.BooleanField(default=0)),
                ('mc_answer', models.CharField(default='', max_length=1)),
                ('sa_answer', models.CharField(default='', max_length=20)),
                ('answer_A', models.CharField(blank=True, max_length=500)),
                ('answer_B', models.CharField(blank=True, max_length=500)),
                ('answer_C', models.CharField(blank=True, max_length=500)),
                ('answer_D', models.CharField(blank=True, max_length=500)),
                ('answer_E', models.CharField(blank=True, max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='published_example_problem', to=settings.AUTH_USER_MODEL)),
                ('parent_exampleproblem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.ExampleProblem')),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
                ('question_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedImageModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
                ('parent_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.ImageModel')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedProblemObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('point_value', models.IntegerField(default=1)),
                ('problem_code', models.TextField(blank=True)),
                ('problem_display', models.TextField(blank=True)),
                ('isProblem', models.BooleanField(default=0)),
                ('mc_answer', models.CharField(blank=True, max_length=1)),
                ('sa_answer', models.CharField(blank=True, max_length=20)),
                ('answer_A', models.CharField(blank=True, max_length=500)),
                ('answer_B', models.CharField(blank=True, max_length=500)),
                ('answer_C', models.CharField(blank=True, max_length=500)),
                ('answer_D', models.CharField(blank=True, max_length=500)),
                ('answer_E', models.CharField(blank=True, max_length=500)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='published_problem_object', to=settings.AUTH_USER_MODEL)),
                ('parent_problemobject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.ProblemObject')),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem')),
                ('question_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.QuestionType')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PublishedProblemSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('default_point_value', models.IntegerField(default=1)),
                ('total_points', models.IntegerField(default=0)),
                ('num_problems', models.IntegerField(default=0)),
                ('parent_problemset', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.ProblemSet')),
                ('problem_objects', models.ManyToManyField(blank=True, to='teacher.PublishedProblemObject')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedProof',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(max_length=20)),
                ('proof_code', models.TextField(blank=True)),
                ('proof_display', models.TextField(blank=True)),
                ('isSolution', models.BooleanField(default=0)),
                ('parent_proof', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.Proof')),
                ('solution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Solution')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedSlide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('order', models.IntegerField(default=0)),
                ('top_order_number', models.IntegerField(default=0)),
                ('parent_slide', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.Slide')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PublishedSlideGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('num_slides', models.IntegerField(default=0)),
                ('parent_slidegroup', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.SlideGroup')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedSlideObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('parent_slideobject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.SlideObject')),
                ('slide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slide_objects', to='teacher.PublishedSlide')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PublishedTextBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_code', models.TextField(blank=True)),
                ('text_display', models.TextField(blank=True)),
                ('parent_textblock', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.TextBlock')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedTheorem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150)),
                ('prefix', models.CharField(max_length=20)),
                ('theorem_code', models.TextField(blank=True)),
                ('theorem_display', models.TextField(blank=True)),
                ('parent_theorem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.Theorem')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField(default=0)),
                ('total_points', models.IntegerField(default=0)),
                ('num_problems', models.IntegerField(default=0)),
                ('num_problemsets', models.IntegerField(default=0)),
                ('parent_unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='PublishedUnitObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('parent_unitobject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teacher.UnitObject')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_objects', to='teacher.PublishedUnit')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='publishedslidegroup',
            name='unit_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedUnitObject'),
        ),
        migrations.AddField(
            model_name='publishedslide',
            name='slidegroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slides', to='teacher.PublishedSlideGroup'),
        ),
        migrations.AddField(
            model_name='publishedproblemset',
            name='unit_object',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.PublishedUnitObject'),
        ),
        migrations.AddField(
            model_name='publishedclass',
            name='pub_units',
            field=models.ManyToManyField(blank=True, to='teacher.PublishedUnit'),
        ),
    ]