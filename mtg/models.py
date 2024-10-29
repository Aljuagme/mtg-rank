from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
class User(AbstractUser):

    def total_played(self):
        count = 0
        for deck in self.decks.all():
            matches = Match.objects.filter(models.Q(deck1=deck) | models.Q(deck2=deck))
            count += matches.count()
        return count

    def wins(self):
        if self.decks.count() != 0:
            wins = sum([deck.wins_count for deck in self.decks.all()])
            return wins
        return 0


    def win_ratio(self):
        if self.decks.count() != 0:
            total_win_ratio = sum([deck.win_ratio() for deck in self.decks.all()])
            avg_win_ratio = total_win_ratio / self.decks.count()
            return avg_win_ratio
        return 0

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "total_matches": self.total_played(),
            "wins": self.wins(),
            "win_ratio": self.win_ratio()
        }


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
        matches = Match.objects.filter(models.Q(deck1=self) | models.Q(deck2=self))
        self.wins_count = matches.filter(winner=self).count()
        self.losses_count = matches.exclude(winner=self).count() - matches.filter(winner=None).count()
        self.total_matches_count = matches.count()
        # self.total_matches_count = Match.objects.filter(models.Q(deck1=self) | models.Q(deck2=self)).count()
        self.save()

    def win_ratio(self):
        total = self.total_matches_count
        return 0 if total == 0 else round((self.wins_count / self.total_matches_count) * 100, 1)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "ownerId": self.user.id,
            "owner": self.user.username,
            "category": self.get_category_display(),
            "wins": self.wins_count,
            "losses": self.losses_count,
            "draws": self.total_matches_count - (self.wins_count + self.losses_count),
            "total_matches": self.total_matches_count,
            "win_ratio": self.win_ratio(),
            "rivals": [{
                "id": rival.id,
                "name": rival.name,
                "owner": {
                    "id": rival.user.id,
                    "username": rival.user.username,
                },
                "stats": self.stats_vs_rival(rival)
            } for rival in self.get_rivals()]
        }

    def get_rivals(self):
        rivals = Deck.objects.filter(
            models.Q(matches_as_deck1__deck2=self) | models.Q(matches_as_deck2__deck1=self)
        ).distinct()

        r = []
        for rival in rivals:
            win_ratio = self.stats_vs_rival(rival)["win_ratio"]
            r.append((rival, win_ratio))

        sorted_rivals = sorted(r, key=lambda x: x[1], reverse=True)

        return [rivals[0] for rivals in sorted_rivals]


    def stats_vs_rival(self, rival):
        matches = Match.objects.filter(
            models.Q(deck1=self) & models.Q(deck2=rival) | models.Q(deck1=rival) & models.Q(deck2=self)
        )
        total = matches.count()
        wins = matches.filter(winner=self).count()
        losses = matches.filter(winner=rival).count()
        draws = total - wins - losses
        return {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total": total,
            "win_ratio": 0 if total==0 else round((wins / total) * 100, 1),
            "category": self.get_category_display()
        }


    def __str__(self):
        return f" {self.id} - {self.name}: {self.get_category_display()}. Win-Ratio: {self.win_ratio()}"



class Match(models.Model):
    class Result(models.TextChoices):
        ABSOLUTE_WIN = "AW", "2-0"
        WIN = "WN", "2-1"
        DRAW = "DW", "1-1"
        LOSS = "LS", "1-2"
        ABSOLUTE_LOSS = "AL", "0-2"

    class Meta:
        ordering = ("-date_played", )

    deck1 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_as_deck1')
    deck2 = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_as_deck2')
    winner = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='matches_won', blank=True, null=True)
    result = models.CharField(choices=Result.choices, default=Result.ABSOLUTE_WIN, max_length=2)
    date_played = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
         Ensure that:
         - A deck cannot play against itself.
         - The winner corresponds with the result.
         """
        if self.deck1 == self.deck2:
            raise ValidationError("A deck cannot compete against itself.")

        # If result is not DRAW, winner must be either deck1 or deck2 based on result
        if self.result == self.Result.DRAW:
            if self.winner is not None:
                raise ValidationError("There must be no winner for a draw.")
        elif self.result in [self.Result.ABSOLUTE_WIN, self.Result.WIN] and self.winner != self.deck1:
            raise ValidationError("Deck1 must be the winner for result 2-0 or 2-1.")
        elif self.result in [self.Result.ABSOLUTE_LOSS, self.Result.LOSS] and self.winner != self.deck2:
            raise ValidationError("Deck2 must be the winner for result 0-2 or 1-2.")


    def save(self, *args, **kwargs):
        if self.result in [self.Result.ABSOLUTE_WIN, self.Result.WIN]:
            self.winner = self.deck1
        elif self.result in [self.Result.ABSOLUTE_LOSS, self.Result.LOSS]:
            self.winner = self.deck2 # Deck1 wins with 2-1
        elif self.result == self.Result.DRAW:
            self.winner = None

        self.clean()

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
        return f"{self.deck1.name} vs {self.deck2.name}. |-> Winner: {self.winner.name if self.winner else 'Draw'}"

    def serialize(self):
        return {
            "id": self.id,
            "deck1": self.deck1.serialize(),
            "deck2": self.deck2.serialize(),
            "date_played": self.date_played.date(),
            "winner": self.winner.name if self.winner else None,
            "result": self.get_result_display(),
        }




