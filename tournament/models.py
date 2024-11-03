from django.db import models


# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=20)
    points = models.IntegerField(default=0)
    match_wins = models.IntegerField(default=0)
    rivals = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
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
        return f"Name: {self.name}. Rivals: {self.rivals}"