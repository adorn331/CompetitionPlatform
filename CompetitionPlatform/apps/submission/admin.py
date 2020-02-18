from django.contrib import admin
from apps.submission.models import Submission


@admin.register(Submission)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'competition', 'participant')
    ordering = ('id',)
