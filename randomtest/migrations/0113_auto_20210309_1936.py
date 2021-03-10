# Generated by Django 2.2.12 on 2021-03-10 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0112_auto_20210309_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer_type',
            field=models.CharField(choices=[('INT', 'Integer'), ('CF', 'Common Fraction'), ('DEC', 'Decimal'), ('MIX', 'Mixed Number'), ('DOL', 'Dollars'), ('WKD', 'Day of the Week'), ('SQR', 'Square Root'), ('RAD', 'Radical (a*sqrt(b))'), ('CFQ', 'Common Fraction in Simplest Radical Form (a*sqrt(b)/c)'), ('SQS', 'Sum of Square Roots (a+b*sqrt(c))'), ('OPR', 'Ordered Pair'), ('TEX', 'Text'), ('PCT', 'Percent')], default='INT', max_length=3),
        ),
    ]