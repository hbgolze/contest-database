# Generated by Django 2.2.8 on 2019-12-12 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('handouts', '0009_auto_20170925_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentelement',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
