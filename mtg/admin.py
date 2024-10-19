from django.contrib import admin
from mtg.models import User, Deck, Match


# Register your models here.
class DeckInline(admin.TabularInline):  # or use admin.StackedInline for a different layout
    model = Deck
    extra = 1  # Number of blank forms to display for adding new Deck instances
    fields = ['name', 'category']  # Specify which fields to display in the inline form

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined']  # Display these fields in the admin user list
    inlines = [DeckInline]  # Include DeckInline to manage decks from the User admin page

class DeckAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "user", "wins_count", "total_matches_count"]
    search_fields = ["name", "user__username"]

class MatchAdmin(admin.ModelAdmin):
    list_display = ["deck1", "result", "deck2", "winner"]


admin.site.register(User, UserAdmin)
admin.site.register(Deck, DeckAdmin)
admin.site.register(Match, MatchAdmin)