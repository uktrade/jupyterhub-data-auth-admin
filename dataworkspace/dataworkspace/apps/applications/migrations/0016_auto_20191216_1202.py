# Generated by Django 2.2.8 on 2019-12-16 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('applications', '0015_applicationinstancedbusers')]

    operations = [
        migrations.AddIndex(
            model_name='applicationinstancedbusers',
            index=models.Index(
                fields=['db_username'], name='application_db_user_1e30c1_idx'
            ),
        )
    ]