# Generated by Django 2.2.7 on 2020-03-03 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isactivate',
            field=models.BooleanField(default=False),
        ),
    ]
