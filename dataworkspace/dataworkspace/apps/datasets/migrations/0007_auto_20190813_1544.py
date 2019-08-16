# Generated by Django 2.2.3 on 2019-08-13 15:44

from django.db import migrations


def generate_column_name(apps, _):
    model = apps.get_model('datasets', 'ReferenceDatasetField')
    for field in model.objects.all():
        field.column_name = 'field_{}'.format(field.id)
        field.save()


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0006_auto_20190813_1544'),
    ]

    operations = [
        migrations.RunPython(
            generate_column_name, reverse_code=migrations.RunPython.noop
        )
    ]
