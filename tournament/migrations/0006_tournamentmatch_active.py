# Generated by Django 5.1.2 on 2024-11-04 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_rename_round_tournamentmatch_n_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentmatch',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
