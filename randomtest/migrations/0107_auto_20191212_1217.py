# Generated by Django 2.2.8 on 2019-12-12 18:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomtest', '0106_contesttest_short_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaboratorrequest',
            name='from_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collab_invitations_from', to='randomtest.UserProfile'),
        ),
        migrations.AlterField(
            model_name='collaboratorrequest',
            name='to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collab_invitations_to', to='randomtest.UserProfile'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='newresponse',
            name='usertest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newresponses', to='randomtest.UserTest'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='approval_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='problem',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='problem',
            name='question_type_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='question_type_new', to='randomtest.QuestionType'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problems', to='randomtest.Round'),
        ),
        migrations.AlterField(
            model_name='problemapproval',
            name='approval_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='proofresponse',
            name='problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Problem'),
        ),
        migrations.AlterField(
            model_name='responses',
            name='test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='randomtest.Test'),
        ),
        migrations.AlterField(
            model_name='usertest',
            name='responses',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usertest', to='randomtest.Responses'),
        ),
    ]