from django.db import models
from django.contrib.postgres.fields import JSONField


class Participant(models.Model):
    name = models.CharField(max_length=64)
    pno = models.CharField(max_length=64)
    province = models.CharField(max_length=32)
    school = models.CharField(max_length=32)
    grade = models.CharField(max_length=32)
    id_num = models.CharField(max_length=32)

    def get_submission(self, competition):
        from apps.submission.models import Submission
        return Submission.objects.filter(participant=self, competition=competition).first()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    submission_standard = JSONField()
    participants = models.ManyToManyField(to=Participant, related_name='participated_competitions')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
