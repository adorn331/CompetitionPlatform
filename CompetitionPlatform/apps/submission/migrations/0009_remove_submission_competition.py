# Generated by Django 2.2.7 on 2020-03-02 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0008_auto_20200225_1004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='competition',
        ),
    ]
