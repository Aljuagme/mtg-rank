from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=20)
    points = models.IntegerField(default=0)
    match_wins = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def deactivate(self):
        self.active = False
        self.save()
        return self

    def activate(self):
        self.active = True
        self.save()
        return self

    def __str__(self):
        return f"Name: {self.name}. Rivals: {[rival.name for rival in self.get_rivals()]}"

    def get_rivals(self):
        rivals = Player.objects.filter(
            models.Q(matches_as_player1__player2=self) | models.Q(matches_as_player2__player1=self),
        ).distinct()

        return rivals

    def serialize(self):

        return {
            "id": self.id,
            "name": self.name,
            "points": self.points,
            "match_wins": self.match_wins,
        }


class TournamentMatch(models.Model):
    class Result(models.TextChoices):
        ABSOLUTE_WIN = "AW", "2-0"
        WIN = "WN", "2-1"
        DRAW = "DW", "1-1"
        LOSS = "LS", "1-2"
        ABSOLUTE_LOSS = "AL", "0-2"

    class Meta:
        ordering = ("-date_played", )

    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_player1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_as_player2')
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches_won', blank=True, null=True)
    result = models.CharField(choices=Result.choices, default=Result.ABSOLUTE_WIN, max_length=2)
    n_round = models.IntegerField()
    active = models.BooleanField(default=True)
    date_played = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
         Ensure that:
         - A deck cannot play against itself.
         - The winner corresponds with the result.
         """
        if self.player1 == self.player2:
            raise ValidationError("A deck cannot compete against itself.")

        # If result is not DRAW, winner must be either deck1 or deck2 based on result
        if self.result == self.Result.DRAW:
            if self.winner is not None:
                raise ValidationError("There must be no winner for a draw.")
        elif self.result in [self.Result.ABSOLUTE_WIN, self.Result.WIN] and self.winner != self.player1:
            raise ValidationError("Player1 must be the winner for result 2-0 or 2-1.")
        elif self.result in [self.Result.ABSOLUTE_LOSS, self.Result.LOSS] and self.winner != self.player2:
            raise ValidationError("Player2 must be the winner for result 0-2 or 1-2.")


    def save(self, *args, **kwargs):
        if self.result in [self.Result.ABSOLUTE_WIN, self.Result.WIN]:
            self.winner = self.player1
        elif self.result in [self.Result.ABSOLUTE_LOSS, self.Result.LOSS]:
            self.winner = self.player2
        elif self.result == self.Result.DRAW:
            self.winner = None

        self.clean()

        super().save(*args, **kwargs) # We modify the save() to check the equality of decks. That's why super(), to call the father save.


    def __str__(self):
        return f"{self.player1.name} vs {self.player2.name}. |-> Winner: {self.winner.name if self.winner else 'Draw'}"

    def deactivate(self):
        self.active = False
        self.save()
        return self

    def activate(self):
        self.active = True
        self.save()
        return self

    def serialize(self):
        return {
            "id": self.id,
            "player1": self.player1.serialize(),
            "player2": self.player2.serialize(),
            "date_played": self.date_played.date(),
            "winner": self.winner.name if self.winner else None,
            "result": self.get_result_display(),
        }