# Generated by Django 5.1.2 on 2024-11-05 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0006_tournamentmatch_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='match_losses',
            field=models.IntegerField(default=0),
        ),
    ]