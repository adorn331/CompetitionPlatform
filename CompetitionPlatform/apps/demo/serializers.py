from apps.demo.models import People
from rest_framework.serializers import ModelSerializer


class PeopleSerializer(ModelSerializer):
    class Meta:
        model = People
        fields = ['name', ]
