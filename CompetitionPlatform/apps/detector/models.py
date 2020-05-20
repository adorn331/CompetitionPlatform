from django.db import models
from apps.competition.models import Competition
from apps.submission.models import Submission


# 相似度记录
class Similarity(models.Model):
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE, related_name='similarity') # 所在比赛

    src_submission = models.ForeignKey(to=Submission, on_delete=models.CASCADE, related_name='src_sub') # 源选手提交
    src_file = models.CharField(max_length=64)  # 源文件

    dest_submission = models.ForeignKey(to=Submission, on_delete=models.CASCADE, related_name='dest_sub') # 被比对的选手提交
    dest_file = models.CharField(max_length=64) # 被比对的文件

    percentage = models.IntegerField() # 相似百分比
