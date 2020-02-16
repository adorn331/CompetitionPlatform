from django.db import models
from django.contrib.postgres.fields import JSONField


class Participant(models.Model):
    pid = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    gender = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    submission_standard = JSONField()
    participants = models.ManyToManyField(to=Participant, related_name='participated_competitions')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
