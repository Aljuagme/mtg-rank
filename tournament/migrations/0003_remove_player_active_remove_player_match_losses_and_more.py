# Generated by Django 5.1.2 on 2024-11-19 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0002_tournament_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='active',
        ),
        migrations.RemoveField(
            model_name='player',
            name='match_losses',
        ),
        migrations.RemoveField(
            model_name='player',
            name='match_wins',
        ),
        migrations.RemoveField(
            model_name='player',
            name='points',
        ),
        migrations.RemoveField(
            model_name='player',
            name='tournament',
        ),
        migrations.CreateModel(
            name='PlayerTournamentStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('match_wins', models.IntegerField(default=0)),
                ('match_losses', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_stats', to='tournament.player')),
                ('tournament', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='players_stats', to='tournament.tournament')),
            ],
            options={
                'unique_together': {('player', 'tournament')},
            },
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player1', to='tournament.playertournamentstats'),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='player2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player2', to='tournament.playertournamentstats'),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches_won', to='tournament.playertournamentstats'),
        ),
    ]
