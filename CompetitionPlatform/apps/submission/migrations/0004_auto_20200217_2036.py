# Generated by Django 2.2.7 on 2020-02-17 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0003_auto_20200217_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='bundle',
            field=models.FileField(upload_to='uploads/%Y/%m/%d/'),
        ),
    ]
