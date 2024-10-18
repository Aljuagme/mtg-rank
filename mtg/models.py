from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass


class Deck(models.Model):
    class Category(models.TextChoices):
        STANDARD = 'ST', 'Standard'
        PIONEER = 'Pp', 'Pioneer'
        MODERN = 'Mn', 'Modern'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=20)
    category = models.CharField(max_length=2,
                                choices=Category.choices,
                                default=Category.PIONEER)

    wins_count = models.PositiveIntegerField(default=0)
    losses_count = models.PositiveIntegerField(default=0)
    total_matches_count = models.PositiveIntegerField(default=0)


    def update_stats(self):
        self.wins_count = Match.objects.filter(winner=self).count()
        self.losses_count = Match.objects.filter(
            models.Q(deck1=self) | models.Q(deck2=self), ~models.Q(winner=self)
        ).count()
        self.total_matches_count = self.matches_as_deck1.count() + self.matches_as_deck2.count()
        # self.total_matches_count = Match.objects.filter(models.Q(deck1=self) | models.Q(deck2=self)).count()
        self.save()

    def win_ratio(self):
        total = self.total_matches_count
        return 0 if total == 0 else self.wins_count / self.total_matches_count

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "wins": self.wins_count,
            "losses": self.losses_count,
            "total_matches": self.total_matches_count,
            "win_ratio": self.win_ratio(),
            "rivals": [rival.id for rival in self.get_rivals()]
        }

    def get_rivals(self):
        rivals = Deck.objects.filter(
            models.Q(matches_as_deck1__deck2=self) | models.Q(matches_as_deck2__deck1=self)
        ).distinct()
        return rivals

    def stats_vs_rival(self, rival):
        matches = Match.objects.filter(
            models.Q(deck1=self) & models.Q(deck2=rival) | models.Q(deck1=rival) & models.Q(deck2=self)
        )
        total = matches.count()
        wins = matches.filter(winner=self).count()
        losses = (total - wins) / total
        return {"wins": wins,
                "losses": losses
                }

    def __str__(self):
        return f" {self.id} - {self.name}: {self.get_category_display()}"



class Match(models.Model):
    deck1 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_as_deck1')
    deck2 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_as_deck2')
    winner = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_won')
    date_played = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Prevent deck from playing against itself
        if self.deck1 == self.deck2:
            raise ValueError("A deck cannot compete against itself.")
        super().save(*args, **kwargs) # We modify the save() to check the equality of decks. That's why super(), to call the father save.

        # Update stats for both decks
        self.deck1.update_stats()
        self.deck2.update_stats()


    def delete(self, *args, **kwargs):
        # When a match is deleted, update the stats of both decks and head-to-head
        super().delete(*args, **kwargs)
        self.deck1.update_stats()
        self.deck2.update_stats()

    def __str__(self):
        return f"{self.deck1.name} vs {self.deck2.name}. |-> Winner: {self.winner.name}"


class HeadToHead(models.Model):
    deck1 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='head_to_head_as_deck1')
    deck2 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='head_to_head_as_deck2')




