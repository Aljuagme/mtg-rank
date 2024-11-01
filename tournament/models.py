from django.db import models


# Create your models here.
class Players(models.Model):
    name = models.CharField(max_length=20)
    points = models.IntegerField(default=0)
    match_wins = models.IntegerField(default=0)
    rivals = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

