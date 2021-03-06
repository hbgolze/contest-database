# Generated by Django 2.2.12 on 2021-03-08 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mocktests', '0003_auto_20210306_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='MockTestSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('segment_type', models.CharField(max_length=2)),
                ('instructions', models.CharField(max_length=1000)),
                ('time_limit', models.DurationField(null=True)),
                ('order', models.IntegerField(default=0)),
                ('mock_test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mock_test_segments', to='mocktests.MockTest')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='UserMockTestSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.FloatField(default=0)),
                ('status', models.IntegerField(default=0)),
                ('start_time', models.TimeField(null=True)),
                ('end_time', models.TimeField(null=True)),
                ('order', models.IntegerField(default=0)),
                ('user_mock_test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mocktests.UserMockTest')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.RemoveField(
            model_name='usermocktestobject',
            name='mock_test_round',
        ),
        migrations.RemoveField(
            model_name='usermocktestobject',
            name='user_mock_test',
        ),
        migrations.RemoveField(
            model_name='mocktestproblem',
            name='mocktest_round',
        ),
        migrations.RemoveField(
            model_name='usermockproblem',
            name='user_mocktest_round',
        ),
        migrations.DeleteModel(
            name='MockTestObject',
        ),
        migrations.DeleteModel(
            name='UserMockTestObject',
        ),
    ]
