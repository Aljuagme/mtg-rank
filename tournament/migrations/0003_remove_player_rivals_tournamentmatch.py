# Generated by Django 5.1.2 on 2024-11-04 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0002_player_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='rivals',
        ),
        migrations.CreateModel(
            name='TournamentMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(choices=[('AW', '2-0'), ('WN', '2-1'), ('DW', '1-1'), ('LS', '1-2'), ('AL', '0-2')], default='AW', max_length=2)),
                ('date_played', models.DateTimeField(auto_now_add=True)),
                ('player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player1', to='tournament.player')),
                ('player2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player2', to='tournament.player')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches_won', to='tournament.player')),
            ],
            options={
                'ordering': ('-date_played',),
            },
        ),
    ]
