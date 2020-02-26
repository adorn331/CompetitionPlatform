from django.db import models
from apps.competition.models import Competition, Participant
from django.contrib.postgres.fields import JSONField


def origin_bundle_path(instance, filename):
    return f'uploads/{instance.competition.id}/{instance.participant.id}/origin/{filename}'


def filtered_bundle_path(instance, filename):
    return f'uploads/{instance.competition.id}/{instance.participant.id}/filtered/{filename}'


class Submission(models.Model):
    bundle = models.FileField(upload_to=origin_bundle_path)
    filtered_bundle = models.FileField(upload_to=filtered_bundle_path)
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE)
    participant = models.ForeignKey(to=Participant, on_delete=models.CASCADE)
    valid = models.BooleanField(default=False)
    bundle_structure = JSONField(blank=True, null=True)
    missing_files = JSONField(blank=True, null=True)

