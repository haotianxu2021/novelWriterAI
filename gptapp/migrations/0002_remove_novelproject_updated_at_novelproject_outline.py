# Generated by Django 5.0.6 on 2024-07-08 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gptapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='novelproject',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='novelproject',
            name='outline',
            field=models.IntegerField(default=0),
        ),
    ]
