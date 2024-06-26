# Generated by Django 3.2.23 on 2024-04-15 05:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0120_auto_20231218_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelayProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=2024)),
                ('form_letter', models.CharField(blank=True, max_length=2)),
                ('is_backwards', models.BooleanField(default=0)),
                ('label', models.CharField(blank=True, max_length=20)),
                ('readable_label', models.CharField(blank=True, max_length=20)),
                ('problem_text_1', models.TextField(blank=True)),
                ('display_problem_text_1', models.TextField(blank=True)),
                ('problem_text_2', models.TextField(blank=True)),
                ('display_problem_text_2', models.TextField(blank=True)),
                ('problem_text_3', models.TextField(blank=True)),
                ('display_problem_text_3', models.TextField(blank=True)),
                ('answer_1', models.CharField(blank=True, max_length=150)),
                ('answer_2', models.CharField(blank=True, max_length=150)),
                ('backwards_answer_2', models.CharField(blank=True, max_length=150)),
                ('answer_3', models.CharField(blank=True, max_length=150)),
                ('backwards_answer_3', models.CharField(blank=True, max_length=150)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['label'],
            },
        ),
    ]
