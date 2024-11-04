# Generated by Django 5.1.2 on 2024-10-19 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtg', '0002_alter_headtohead_unique_together_match_result_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='winner',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matches_won', to='mtg.deck'),
        ),
    ]