from django.db import models
from django.contrib.postgres.fields import JSONField


class Competition(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    submission_standard = JSONField()

    submission_path = models.CharField(max_length=64, default='/xxx/yyy') # todo get a valid default?

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(max_length=64)
    pno = models.CharField(max_length=64)
    province = models.CharField(max_length=32)
    school = models.CharField(max_length=32)
    grade = models.CharField(max_length=32)
    id_num = models.CharField(max_length=32)

    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE, related_name='participants')

    host = models.CharField(max_length=64, blank=True, null=True)
    position = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name