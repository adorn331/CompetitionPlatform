from django.db import models
from apps.competition.models import Competition
from apps.submission.models import Submission


# Create your models here.
class Similarity(models.Model):
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE, related_name='similarity')
    src_submission = models.ForeignKey(to=Submission, on_delete=models.CASCADE)
    dest_submission = models.ForeignKey(to=Submission, on_delete=models.CASCADE)
    percentage = models.FloatField()
