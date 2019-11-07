# Generated by Django 2.2.3 on 2019-08-19 12:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('datasets', '0008_auto_20190813_1544')]

    operations = [
        migrations.AlterField(
            model_name='referencedataset',
            name='table_name',
            field=models.CharField(
                help_text='Descriptive table name for the field - Note: Must start with "ref_" and contain only lowercase letters, numbers and underscores',
                max_length=255,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Table names must be prefixed with "ref_" and can contain only lowercase letters, numbers and underscores',
                        regex='^ref_[a-z0-9_]*$',
                    )
                ],
                verbose_name='Table name',
            ),
        )
    ]
