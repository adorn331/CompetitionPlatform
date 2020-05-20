from django.db import models
from apps.competition.models import Competition, Participant
from django.contrib.postgres.fields import JSONField


def origin_bundle_path(instance, filename):
    return f'uploads/{instance.participant.competition.id}/{instance.participant.id}/origin/{filename}'


def filtered_bundle_path(instance, filename):
    return f'uploads/{instance.participant.competition.id}/{instance.participant.id}/filtered/{filename}'


# 选手的提交
class Submission(models.Model):
    bundle = models.FileField(upload_to=origin_bundle_path) # 选手提交压缩包的相对路径
    filtered_bundle = models.FileField(upload_to=filtered_bundle_path)  # 已过滤的包相对路径
    participant = models.ForeignKey(to=Participant, on_delete=models.CASCADE, related_name='uploaded_submission')   # 提交者
    status = models.CharField(max_length=64, default='已提交，校验中..')   # 状态
    bundle_structure = JSONField(blank=True, null=True)  # 包内文件结构
    missing_files = JSONField(blank=True, null=True)    # 相对于标准所缺文件
