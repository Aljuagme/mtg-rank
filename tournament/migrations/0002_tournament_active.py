# Generated by Django 5.1.2 on 2024-11-16 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
