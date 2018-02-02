# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-02-01 06:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0082_auto_20180131_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollaboratorRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('accepted', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_invitations_from', to='randomtest.UserProfile')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collab_invitations_to', to='randomtest.UserProfile')),
            ],
        ),
    ]
