# Generated by Django 2.2.12 on 2023-03-22 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0116_problemgroup_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='calculator',
            field=models.BooleanField(default=0),
        ),
    ]