from django.contrib import admin
from tournament.models import Player, TournamentMatch

# Register your models here.

admin.site.register(Player)
admin.site.register(TournamentMatch)