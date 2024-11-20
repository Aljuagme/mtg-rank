from django.contrib import admin
from tournament.models import Player, PlayerTournamentStats, TournamentMatch, Tournament

# Register your models here.
class PlayerTournamentStatsInline(admin.TabularInline):
    model = PlayerTournamentStats
    extra = 0
    fields = ["player"]


class TournamentAdmin(admin.ModelAdmin):
    list_display = ["id", "active"]
    inlines = [PlayerTournamentStatsInline]



admin.site.register(Player)
admin.site.register(PlayerTournamentStats)
admin.site.register(TournamentMatch)
admin.site.register(Tournament, TournamentAdmin)