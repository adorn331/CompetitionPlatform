from django.contrib import admin
from apps.competition.models import Participant, Competition


@admin.register(Participant)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'pid', 'name')
    ordering = ('id',)


@admin.register(Competition)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_time')
    ordering = ('-created_time',)
