# Generated by Django 3.0.3 on 2020-03-09 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('applications', '0019_auto_20200306_1126')]

    operations = [
        migrations.AddField(
            model_name='applicationtemplate',
            name='gitlab_project_id',
            field=models.IntegerField(
                help_text='The ID of the corresponding project in GitLab',
                null=True,
                unique=True,
            ),
        )
    ]
