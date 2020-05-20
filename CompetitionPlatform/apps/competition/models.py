from django.db import models
from django.contrib.postgres.fields import JSONField


# 考场信息
class Room(models.Model):
    name = models.CharField(max_length=64, unique=True)  # 考场名
    layout_matrix = models.CharField(max_length=512)  # 布局矩阵


# 赛事信息
class Competition(models.Model):
    name = models.CharField(max_length=64, unique=True)  # 竞赛名
    description = models.TextField(blank=True, null=True)  # 描述
    created_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    submission_standard = JSONField()  # 标准提交格式

    submission_path = models.CharField(max_length=64)  # 选手存放路径
    room_layout = models.ForeignKey(to=Room, on_delete=models.PROTECT)  # 使用考场

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


# 参赛者
class Participant(models.Model):
    name = models.CharField(max_length=64)  # 参赛者名
    pno = models.CharField(max_length=64)   # 考号
    province = models.CharField(max_length=32)  # 省份
    school = models.CharField(max_length=32)    # 学校
    grade = models.CharField(max_length=32)     # 年级
    id_num = models.CharField(max_length=32)    # 身份证号

    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE, related_name='participants')  # 所属比赛

    host = models.CharField(max_length=64, blank=True, null=True)   # 选手主机
    position = models.CharField(max_length=16, blank=True, null=True)   # 选手座位号

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
