from django.contrib import admin

# Register your models here.
from apps.detector.models import Similarity


@admin.register(Similarity)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'percentage')
    ordering = ('id',)
