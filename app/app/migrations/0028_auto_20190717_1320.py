# Generated by Django 2.2.3 on 2019-07-17 13:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20190717_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencedatasetfield',
            name='name',
            field=models.CharField(help_text='Field name must start with a letter and may only contain lowercase letters numbers and underscores (no spaces)', max_length=60, validators=[django.core.validators.RegexValidator(message='Please only enter lowercase letters, numbers and underscores', regex='^[a-z][a-z0-9_\\.]*$')]),
        ),
    ]