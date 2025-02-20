# Generated by Django 2.2.7 on 2020-03-01 23:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0007_auto_20200220_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='participants',
        ),
        migrations.AddField(
            model_name='participant',
            name='competition',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='competition.Competition'),
            preserve_default=False,
        ),
    ]
