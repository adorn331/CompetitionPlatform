from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # demo field for later extensions
    nick_name = models.CharField(max_length=50, blank=True)
    isactivate = models.BooleanField(default=False)


    class Meta(AbstractUser.Meta):
        pass

    # 元数据 增强可读性
    class Meta:
        verbose_name = '用户'
        ordering = ['-id']

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username
